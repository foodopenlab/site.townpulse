from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import (
    RegionOrm,
    SnapBuildingOrm,
    SnapPopulationOrm,
    SnapStatisticsOrm,
    SnapTransportOrm,
    TviScoreOrm,
    VillageOrm,
)
from apps.townpulse.adapter.outbound.orm_mappers.tvi_score_orm_mapper import TviScoreOrmMapper
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.domain.entities.tvi_score_entity import TviScoreEntity
from apps.townpulse.services.tvi_calculator import (
    calculate_bus_interval_score,
    calculate_pop_decline_raw,
    calculate_tvi,
    calculate_vacancy_score,
    grade_from_score,
    normalize_min_max,
)


class TviScoreRepository(TviScorePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> TviScoreEntity | None:
        row = (
            await self._session.execute(select(TviScoreOrm).where(TviScoreOrm.id == entity_id))
        ).scalar_one_or_none()
        if not row:
            return None
        return TviScoreOrmMapper.to_entity(row)

    async def find_latest_by_village(self, village_id: UUID) -> TviScoreEntity | None:
        row = (
            await self._session.execute(
                select(TviScoreOrm)
                .where(TviScoreOrm.village_id == village_id)
                .order_by(desc(TviScoreOrm.calculated_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        return TviScoreOrmMapper.to_entity(row) if row else None

    async def find_all_latest(
        self, grade_filter: str | None = None, sigun_filter: str | None = None
    ) -> list[TviScoreEntity]:
        subq = (
            select(TviScoreOrm.village_id, func.max(TviScoreOrm.calculated_at).label("max_date"))
            .group_by(TviScoreOrm.village_id)
            .subquery()
        )
        stmt = (
            select(TviScoreOrm)
            .join(
                subq,
                (TviScoreOrm.village_id == subq.c.village_id) & (TviScoreOrm.calculated_at == subq.c.max_date),
            )
            .join(VillageOrm, VillageOrm.id == TviScoreOrm.village_id)
            .join(RegionOrm, RegionOrm.id == VillageOrm.region_id)
        )
        if grade_filter:
            stmt = stmt.where(TviScoreOrm.risk_level == grade_filter)
        if sigun_filter:
            stmt = stmt.where(RegionOrm.sigungu.contains(sigun_filter))
        rows = (await self._session.execute(stmt)).scalars().all()
        return [TviScoreOrmMapper.to_entity(r) for r in rows]

    async def find_danger_villages(self, threshold: float = 30.0) -> list[TviScoreEntity]:
        subq = (
            select(TviScoreOrm.village_id, func.max(TviScoreOrm.calculated_at).label("max_date"))
            .group_by(TviScoreOrm.village_id)
            .subquery()
        )
        stmt = (
            select(TviScoreOrm)
            .join(
                subq,
                (TviScoreOrm.village_id == subq.c.village_id) & (TviScoreOrm.calculated_at == subq.c.max_date),
            )
            .where(TviScoreOrm.risk_level == "danger")
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return [TviScoreOrmMapper.to_entity(r) for r in rows]

    async def recalculate_all(self) -> int:
        return await _recalculate_all(self._session)


async def recalculate_all(session: AsyncSession) -> int:
    """Backward-compatible module helper — prefer TviScorePort.recalculate_all()."""
    return await _recalculate_all(session)


async def _recalculate_all(session: AsyncSession) -> int:
    villages = (await session.execute(select(VillageOrm))).scalars().all()
    raw_scores: list[float] = []
    metrics: list[dict] = []

    for village in villages:
        pop = (
            await session.execute(
                select(SnapPopulationOrm)
                .where(SnapPopulationOrm.village_id == village.id)
                .order_by(desc(SnapPopulationOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        transport = (
            await session.execute(
                select(SnapTransportOrm)
                .where(SnapTransportOrm.village_id == village.id)
                .order_by(desc(SnapTransportOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        stats = (
            await session.execute(
                select(SnapStatisticsOrm)
                .where(SnapStatisticsOrm.village_id == village.id)
                .order_by(desc(SnapStatisticsOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        building = (
            await session.execute(
                select(SnapBuildingOrm)
                .where(SnapBuildingOrm.village_id == village.id)
                .order_by(desc(SnapBuildingOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()

        pop_total = pop.population_total if pop and pop.population_total is not None else 1000
        pop_65 = pop.population_65plus if pop and pop.population_65plus is not None else 200
        pop_youth = pop.population_youth if pop and pop.population_youth is not None else 100
        households = pop.registered_households if pop and pop.registered_households is not None else 500
        net_mig = pop.net_youth_migration if pop and pop.net_youth_migration is not None else -5
        elderly_rate = (
            stats.aging_ratio if stats and stats.aging_ratio is not None else pop_65 / max(pop_total, 1)
        )
        youth_ratio = (
            stats.youth_ratio if stats and stats.youth_ratio is not None else pop_youth / max(pop_total, 1)
        )
        vacancy_rate = (building.residential_buildings or 0) / max(households, 1) * 0.1 if building else 0.1
        pop_change = net_mig / max(households, 1)
        bus_score = calculate_bus_interval_score(
            transport.bus_route_count if transport else None,
            transport.avg_bus_interval_min if transport else None,
            transport.nearest_stop_distance_m if transport else None,
            transport.bus_stops_within_1km if transport else None,
        )
        raw = calculate_pop_decline_raw(pop_change, elderly_rate, youth_ratio, net_mig, households)
        raw_scores.append(raw)
        metrics.append({"village_id": village.id, "raw": raw, "vacancy_rate": vacancy_rate, "bus_score": bus_score})

    if not metrics:
        return 0

    vmin, vmax = min(raw_scores), max(raw_scores)
    updated = 0
    for m in metrics:
        tvi_row = (
            await session.execute(
                select(TviScoreOrm)
                .where(TviScoreOrm.village_id == m["village_id"])
                .order_by(desc(TviScoreOrm.calculated_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        if not tvi_row:
            continue
        pop_norm = normalize_min_max(m["raw"], vmin, vmax)
        vac_score = calculate_vacancy_score(m["vacancy_rate"])
        tvi = calculate_tvi(pop_norm, vac_score, m["bus_score"])
        tvi_row.pop_decline_score = pop_norm
        tvi_row.vacancy_rate = m["vacancy_rate"]
        tvi_row.bus_interval_score = m["bus_score"]
        tvi_row.tvi_score = tvi
        tvi_row.risk_level = grade_from_score(tvi)
        updated += 1
    return updated
