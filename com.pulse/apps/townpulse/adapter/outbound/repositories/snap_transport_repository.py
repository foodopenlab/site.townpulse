from __future__ import annotations

import logging
import math
import os
from datetime import date
from uuid import UUID

logger = logging.getLogger(__name__)

# 시군구 전체 노선 카탈로그는 수천 건 API 호출 → 이벤트 루프 장시간 점유. 개발/MVP 상한.
_DEFAULT_ROUTE_LIMIT = 40

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.townpulse.adapter.outbound.orm.models import SnapTransportOrm, VillageOrm
from apps.townpulse.app.ports.output.snap_transport_port import SnapTransportPort
from apps.townpulse.domain.entities.snap_transport_entity import SnapTransportEntity
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_public_api_client import (
    BUS_ROUTE_INFO_URL,
    BUS_ROUTE_LIST_URL,
    BUS_ROUTE_STOPS_URL,
    BUS_STOP_NEARBY_URL,
    extract_response_items,
    extract_total_count,
    fetch_json,
)


def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


class SnapTransportRepository(SnapTransportPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._city_cache: dict[str, dict] = {}

    async def find_by_id(self, entity_id: UUID) -> SnapTransportEntity | None:
        return None

    async def ingest_for_village(self, village_id: UUID, *, apply_mock: bool = False) -> None:
        bus_key = get_keymaker().get_secret("BUS_ROUTE_API_KEY")
        stop_key = get_keymaker().get_secret("BUS_STOP_API_KEY") or bus_key
        if bus_key:
            await self._ingest_real(village_id, bus_key, stop_key)
            return
        if apply_mock:
            await self._apply_mock_adjustment(village_id)

    async def _ingest_real(self, village_id: UUID, bus_key: str, stop_key: str) -> None:
        stmt = select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.id == village_id)
        village = (await self._session.execute(stmt)).scalar_one_or_none()
        if not village or village.lat is None or village.lng is None:
            return

        city_code = village.region.tago_city_code if village.region else None
        nearest_m, count_1km = await self._aggregate_stop_access(
            village.lat, village.lng, city_code, stop_key
        )
        bus_route_count: int | None = None
        avg_bus_interval_min: float | None = None
        if city_code:
            city_data = await self._get_city_transport_data(city_code, bus_key)
            bus_route_count = len(city_data["route_ids"])
            avg_bus_interval_min = city_data["avg_interval"]

        await self._upsert_snap_row(
            village_id,
            {
                "bus_route_count": bus_route_count,
                "avg_bus_interval_min": avg_bus_interval_min,
                "nearest_stop_distance_m": nearest_m,
                "bus_stops_within_1km": count_1km,
            },
        )

    async def _get_city_transport_data(self, city_code: str, api_key: str) -> dict:
        if city_code in self._city_cache:
            return self._city_cache[city_code]

        route_ids = await self._get_route_no_list(city_code, api_key)
        limit = int(os.getenv("TRANSPORT_ROUTE_LIMIT", str(_DEFAULT_ROUTE_LIMIT)))
        if limit > 0 and len(route_ids) > limit:
            logger.warning(
                "city %s: route catalog capped %d -> %d (TRANSPORT_ROUTE_LIMIT)",
                city_code,
                len(route_ids),
                limit,
            )
            route_ids = route_ids[:limit]
        intervals: list[int] = []
        stop_catalog: dict[str, tuple[float, float]] = {}
        for route_id in route_ids:
            detail = await self._get_route_info(city_code, route_id, api_key)
            interval = detail.get("intervaltime")
            if interval is not None:
                try:
                    intervals.append(int(interval))
                except (TypeError, ValueError):
                    pass
            stops = await self._fetch_all_tago_pages(
                BUS_ROUTE_STOPS_URL,
                {"serviceKey": api_key, "_type": "json", "cityCode": city_code, "routeId": route_id},
            )
            for stop in stops:
                node_id = stop.get("nodeid")
                lat = stop.get("gpslati")
                lng = stop.get("gpslong")
                if node_id and lat is not None and lng is not None:
                    stop_catalog[str(node_id)] = (float(lat), float(lng))

        data = {
            "route_ids": route_ids,
            "avg_interval": sum(intervals) / len(intervals) if intervals else None,
            "stop_catalog": stop_catalog,
        }
        self._city_cache[city_code] = data
        return data

    async def _get_route_no_list(self, city_code: str, api_key: str) -> list[str]:
        rows = await self._fetch_all_tago_pages(
            BUS_ROUTE_LIST_URL,
            {"serviceKey": api_key, "_type": "json", "cityCode": city_code},
        )
        return [str(r["routeid"]) for r in rows if r.get("routeid")]

    async def _get_route_info(self, city_code: str, route_id: str, api_key: str) -> dict:
        body = await fetch_json(
            BUS_ROUTE_INFO_URL,
            {"serviceKey": api_key, "_type": "json", "cityCode": city_code, "routeId": route_id},
        )
        items = extract_response_items(body)
        return items[0] if items else {}

    async def _fetch_all_tago_pages(self, url: str, base_params: dict, page_size: int = 100) -> list[dict]:
        all_items: list[dict] = []
        page = 1
        while True:
            params = {**base_params, "numOfRows": page_size, "pageNo": page}
            body = await fetch_json(url, params)
            batch = extract_response_items(body)
            if not batch:
                break
            all_items.extend(batch)
            total = extract_total_count(body)
            if total <= 0 or page * page_size >= total:
                break
            page += 1
        return all_items

    async def _fetch_all_nearby_stops(self, lat: float, lng: float, api_key: str) -> list[dict]:
        return await self._fetch_all_tago_pages(
            BUS_STOP_NEARBY_URL,
            {"serviceKey": api_key, "_type": "json", "gpsLati": lat, "gpsLong": lng},
        )

    async def _aggregate_stop_access(
        self, village_lat: float, village_lng: float, city_code: str | None, stop_api_key: str
    ) -> tuple[int | None, int]:
        near_stops = await self._fetch_all_nearby_stops(village_lat, village_lng, stop_api_key)
        catalog: dict[str, tuple[float, float]] = {}
        if city_code:
            bus_key = get_keymaker().get_secret("BUS_ROUTE_API_KEY")
            if bus_key:
                catalog = (await self._get_city_transport_data(city_code, bus_key))["stop_catalog"]

        distances: dict[str, float] = {}
        for stop in near_stops:
            node_id = stop.get("nodeid")
            lat = stop.get("gpslati")
            lng = stop.get("gpslong")
            if node_id and lat is not None and lng is not None:
                distances[str(node_id)] = _haversine_m(village_lat, village_lng, float(lat), float(lng))

        for node_id, (lat, lng) in catalog.items():
            if node_id not in distances:
                distances[node_id] = _haversine_m(village_lat, village_lng, lat, lng)

        if not distances:
            return None, 0
        return round(min(distances.values())), sum(1 for d in distances.values() if d <= 1000)

    async def _upsert_snap_row(self, village_id: UUID, raw: dict) -> None:
        snapshot_date = date.today().replace(day=1)
        existing = (
            await self._session.execute(
                select(SnapTransportOrm)
                .where(SnapTransportOrm.village_id == village_id)
                .order_by(desc(SnapTransportOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()

        fields = (
            "bus_route_count",
            "avg_bus_interval_min",
            "nearest_stop_distance_m",
            "bus_stops_within_1km",
        )
        if existing:
            for field in fields:
                value = raw.get(field)
                if value is not None:
                    setattr(existing, field, value)
            existing.snapshot_date = snapshot_date
        else:
            self._session.add(
                SnapTransportOrm(
                    village_id=village_id,
                    snapshot_date=snapshot_date,
                    bus_route_count=raw.get("bus_route_count"),
                    avg_bus_interval_min=raw.get("avg_bus_interval_min"),
                    nearest_stop_distance_m=raw.get("nearest_stop_distance_m"),
                    bus_stops_within_1km=raw.get("bus_stops_within_1km"),
                )
            )
        await self._session.flush()

    async def _apply_mock_adjustment(self, village_id: UUID) -> None:
        transport = (
            await self._session.execute(
                select(SnapTransportOrm)
                .where(SnapTransportOrm.village_id == village_id)
                .order_by(desc(SnapTransportOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        if not transport:
            return
        transport.nearest_stop_distance_m = min(transport.nearest_stop_distance_m or 500, 800)
        transport.bus_stops_within_1km = max(transport.bus_stops_within_1km or 0, 1)
