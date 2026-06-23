from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.townpulse.adapter.outbound.orm.models import VillageOrm
from apps.townpulse.adapter.outbound.orm_mappers.village_orm_mapper import VillageOrmMapper
from apps.townpulse.app.ports.output.village_port import VillagePort
from apps.townpulse.domain.entities.village_entity import VillageEntity
from apps.townpulse.services.legal_dong_resolver import resolve_village_legal_dong_codes
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_public_api_client import VWORLD_ADDRESS_URL, fetch_json


class VillageRepository(VillagePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> VillageEntity | None:
        stmt = select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.id == entity_id)
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return VillageOrmMapper.to_entity(row) if row else None

    async def find_all(self) -> list[VillageEntity]:
        stmt = select(VillageOrm).options(selectinload(VillageOrm.region)).order_by(VillageOrm.name)
        rows = (await self._session.execute(stmt)).scalars().all()
        return [VillageOrmMapper.to_entity(r) for r in rows]

    async def find_by_code(self, emd_code: str) -> VillageEntity | None:
        stmt = select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.emd_code == emd_code)
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return VillageOrmMapper.to_entity(row) if row else None

    async def find_by_region(self, region_id: UUID) -> list[VillageEntity]:
        stmt = (
            select(VillageOrm)
            .options(selectinload(VillageOrm.region))
            .where(VillageOrm.region_id == region_id)
            .order_by(VillageOrm.name)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [VillageOrmMapper.to_entity(r) for r in rows]

    async def find_all_for_geocode_sync(self) -> list[VillageEntity]:
        rows = (
            await self._session.execute(select(VillageOrm).options(selectinload(VillageOrm.region)))
        ).scalars().all()
        return [VillageOrmMapper.to_entity(r) for r in rows]

    async def update_geocode_from_vworld(self, village_id: UUID) -> None:
        api_key = get_keymaker().get_secret("VWORLD_API_KEY")
        if not api_key:
            return
        stmt = select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.id == village_id)
        village = (await self._session.execute(stmt)).scalar_one_or_none()
        if not village or not village.region:
            return
        address = f"충청북도 {village.region.sigungu} {village.name}"
        params = {
            "service": "address",
            "request": "getcoord",
            "version": "2.0",
            "crs": "epsg:4326",
            "address": address,
            "refine": "true",
            "simple": "false",
            "format": "json",
            "type": "road",
            "key": api_key,
        }
        try:
            body = await fetch_json(VWORLD_ADDRESS_URL, params)
            point = body.get("response", {}).get("result", {}).get("point", {})
            lat = point.get("y")
            lng = point.get("x")
            if lat and lng:
                village.lat = float(lat)
                village.lng = float(lng)
                await self._session.flush()
        except Exception:
            return

    async def resolve_legal_dong_codes(self, household_api_key: str) -> int:
        return await resolve_village_legal_dong_codes(self._session, household_api_key)

    async def update_emd_code(self, village_id: UUID, emd_code: str) -> None:
        row = await self._session.get(VillageOrm, village_id)
        if row:
            row.emd_code = emd_code
            await self._session.flush()
