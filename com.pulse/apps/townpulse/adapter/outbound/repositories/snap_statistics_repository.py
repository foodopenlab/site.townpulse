from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapPopulationOrm, SnapStatisticsOrm, VillageOrm
from apps.townpulse.app.ports.output.snap_statistics_port import SnapStatisticsPort
from apps.townpulse.domain.entities.snap_statistics_entity import SnapStatisticsEntity
from apps.townpulse.services.legal_dong_resolver import current_stats_ym


def _estimate_area_km2(village_name: str) -> float:
    if village_name.endswith("면"):
        return 35.0
    if village_name.endswith("읍"):
        return 25.0
    if village_name.endswith("동"):
        return 8.0
    if village_name.endswith("리"):
        return 5.0
    return 20.0


class SnapStatisticsRepository(SnapStatisticsPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> SnapStatisticsEntity | None:
        return None

    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        village = (
            await self._session.execute(select(VillageOrm).where(VillageOrm.emd_code == legal_dong_code))
        ).scalar_one_or_none()
        if not village:
            return

        pop = (
            await self._session.execute(
                select(SnapPopulationOrm)
                .where(SnapPopulationOrm.village_id == village.id)
                .order_by(desc(SnapPopulationOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        if not pop or not pop.population_total:
            return

        pop_total = max(pop.population_total, 1)
        pop_65 = pop.population_65plus or 0
        pop_youth = pop.population_youth or 0
        area = _estimate_area_km2(village.name)
        raw = {
            "aging_ratio": pop_65 / pop_total,
            "youth_ratio": pop_youth / pop_total,
            "pop_density": pop_total / area,
        }
        await self._upsert_snap_row(village.id, raw)

    async def _upsert_snap_row(self, village_id: UUID, raw: dict) -> None:
        stats_ym = current_stats_ym()
        snapshot_date = date(int(stats_ym[:4]), int(stats_ym[4:6]), 1)
        existing = (
            await self._session.execute(
                select(SnapStatisticsOrm)
                .where(SnapStatisticsOrm.village_id == village_id)
                .order_by(desc(SnapStatisticsOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()

        if existing:
            for field in ("aging_ratio", "youth_ratio", "pop_density"):
                value = raw.get(field)
                if value is not None:
                    setattr(existing, field, value)
            existing.snapshot_date = snapshot_date
        else:
            self._session.add(
                SnapStatisticsOrm(
                    village_id=village_id,
                    snapshot_date=snapshot_date,
                    aging_ratio=raw.get("aging_ratio"),
                    youth_ratio=raw.get("youth_ratio"),
                    pop_density=raw.get("pop_density"),
                )
            )
        await self._session.flush()
