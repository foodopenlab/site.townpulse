from __future__ import annotations

import uuid

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
from apps.townpulse.adapter.outbound.repositories.village_repository import VillageRepository
from apps.townpulse.app.dtos.dashboard_orchestrator_dto import (
    DashboardSummaryDto,
    VillageListItemDto,
    VillageMapSummaryDto,
)
from apps.townpulse.app.ports.output.dashboard_orchestrator_port import DashboardOrchestratorPort
from apps.townpulse.domain.value_objects.tvi_grade_vo import TviGradeVO
from apps.townpulse.services.tvi_calculator import calculate_vacancy_score


class DashboardOrchestratorRepository(DashboardOrchestratorPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._village_repo = VillageRepository(session)

    async def fetch_summary(self) -> DashboardSummaryDto:
        subq = (
            select(TviScoreOrm.village_id, func.max(TviScoreOrm.calculated_at).label("max_date"))
            .group_by(TviScoreOrm.village_id)
            .subquery()
        )
        stmt = select(TviScoreOrm).join(
            subq, (TviScoreOrm.village_id == subq.c.village_id) & (TviScoreOrm.calculated_at == subq.c.max_date)
        )
        scores = (await self._session.execute(stmt)).scalars().all()
        danger = sum(1 for s in scores if s.risk_level == "danger")
        warning = sum(1 for s in scores if s.risk_level == "warning")
        safe = sum(1 for s in scores if s.risk_level == "safe")
        transport_gap = sum(1 for s in scores if (s.bus_interval_score or 0) == 0)

        top5_stmt = (
            select(VillageOrm, TviScoreOrm, RegionOrm)
            .join(TviScoreOrm, TviScoreOrm.village_id == VillageOrm.id)
            .join(RegionOrm, RegionOrm.id == VillageOrm.region_id)
            .join(subq, (TviScoreOrm.village_id == subq.c.village_id) & (TviScoreOrm.calculated_at == subq.c.max_date))
            .order_by(TviScoreOrm.tvi_score.asc())
            .limit(5)
        )
        top5_rows = (await self._session.execute(top5_stmt)).all()
        top5 = []
        for v, t, r in top5_rows:
            pop = (
                await self._session.execute(
                    select(SnapPopulationOrm)
                    .where(SnapPopulationOrm.village_id == v.id)
                    .order_by(desc(SnapPopulationOrm.snapshot_date))
                    .limit(1)
                )
            ).scalar_one_or_none()
            stats = (
                await self._session.execute(
                    select(SnapStatisticsOrm)
                    .where(SnapStatisticsOrm.village_id == v.id)
                    .order_by(desc(SnapStatisticsOrm.snapshot_date))
                    .limit(1)
                )
            ).scalar_one_or_none()
            top5.append(self._build_top5_item(v, t, r, pop, stats))
        vacant_total = await self._session.scalar(
            select(func.coalesce(func.sum(SnapBuildingOrm.residential_buildings), 0))
        )
        total = await self._session.scalar(select(func.count()).select_from(VillageOrm))
        return DashboardSummaryDto(
            total_villages=total or 0,
            danger_count=danger,
            warning_count=warning,
            safe_count=safe,
            total_vacant_houses=int((vacant_total or 0) * 0.15),
            transport_gap_count=transport_gap,
            top5_danger_villages=top5,
            grade_changed_this_month=0,
            pending_prescription_count=0,
        )

    async def fetch_map_villages(self, grade: str | None, sigun: str | None) -> list[VillageListItemDto]:
        subq = (
            select(TviScoreOrm.village_id, func.max(TviScoreOrm.calculated_at).label("max_date"))
            .group_by(TviScoreOrm.village_id)
            .subquery()
        )
        transport_subq = (
            select(
                SnapTransportOrm.village_id,
                func.max(SnapTransportOrm.snapshot_date).label("max_date"),
            )
            .group_by(SnapTransportOrm.village_id)
            .subquery()
        )
        stmt = (
            select(VillageOrm, TviScoreOrm, RegionOrm, SnapTransportOrm)
            .join(TviScoreOrm, TviScoreOrm.village_id == VillageOrm.id)
            .join(RegionOrm, RegionOrm.id == VillageOrm.region_id)
            .join(subq, (TviScoreOrm.village_id == subq.c.village_id) & (TviScoreOrm.calculated_at == subq.c.max_date))
            .outerjoin(transport_subq, transport_subq.c.village_id == VillageOrm.id)
            .outerjoin(
                SnapTransportOrm,
                (SnapTransportOrm.village_id == transport_subq.c.village_id)
                & (SnapTransportOrm.snapshot_date == transport_subq.c.max_date),
            )
        )
        if grade:
            stmt = stmt.where(TviScoreOrm.risk_level == grade)
        if sigun:
            stmt = stmt.where(RegionOrm.sigungu.contains(sigun))
        rows = (await self._session.execute(stmt)).all()
        village_ids = [village.id for village, *_ in rows]
        pop_map, stats_map = await self._latest_pop_and_stats_maps(village_ids)
        items = []
        for village, tvi, region, transport in rows:
            tvi_grade = TviGradeVO.from_risk_level(tvi.risk_level)
            pop = pop_map.get(village.id)
            stats = stats_map.get(village.id)
            pop_change_pct = None
            if pop and pop.net_youth_migration is not None and pop.registered_households:
                pop_change_pct = (pop.net_youth_migration / max(pop.registered_households, 1)) * 100
            vacancy_score = None
            if tvi.vacancy_rate is not None:
                vacancy_score = calculate_vacancy_score(tvi.vacancy_rate) * 100
            items.append(
                VillageListItemDto(
                    village_id=str(village.id),
                    village_code=village.emd_code,
                    village_name=village.name,
                    sigun_name=region.sigungu,
                    tvi_score=tvi.tvi_score,
                    tvi_grade=tvi_grade.grade,
                    tvi_label=tvi_grade.label,
                    color_hex=tvi_grade.color_hex,
                    lat=village.lat or 36.6,
                    lng=village.lng or 127.5,
                    bus_interval_score=tvi.bus_interval_score,
                    nearest_stop_distance_m=transport.nearest_stop_distance_m if transport else None,
                    annual_pop_change_rate=pop_change_pct,
                    net_youth_migration=pop.net_youth_migration if pop else None,
                    vacancy_score=vacancy_score,
                    aging_ratio=stats.aging_ratio if stats else None,
                )
            )
        return items

    async def fetch_village_summary_card(self, village_code: str) -> VillageMapSummaryDto | None:
        village_entity = await self._village_repo.find_by_code(village_code)
        if not village_entity:
            return None
        snaps = await self._fetch_latest_snapshots(village_entity.id)
        tvi = snaps["tvi"]
        transport = snaps["transport"]
        return VillageMapSummaryDto(
            village_code=village_entity.emd_code,
            village_name=village_entity.name,
            tvi_score=tvi.tvi_score if tvi else 0,
            tvi_grade=tvi.risk_level if tvi else "safe",
            nearest_stop_distance_m=transport.nearest_stop_distance_m if transport else None,
            bus_stops_within_1km=transport.bus_stops_within_1km if transport else None,
        )

    async def _fetch_latest_snapshots(self, village_id: uuid.UUID) -> dict:
        pop = (
            await self._session.execute(
                select(SnapPopulationOrm)
                .where(SnapPopulationOrm.village_id == village_id)
                .order_by(desc(SnapPopulationOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        building = (
            await self._session.execute(
                select(SnapBuildingOrm)
                .where(SnapBuildingOrm.village_id == village_id)
                .order_by(desc(SnapBuildingOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        transport = (
            await self._session.execute(
                select(SnapTransportOrm)
                .where(SnapTransportOrm.village_id == village_id)
                .order_by(desc(SnapTransportOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        stats = (
            await self._session.execute(
                select(SnapStatisticsOrm)
                .where(SnapStatisticsOrm.village_id == village_id)
                .order_by(desc(SnapStatisticsOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()
        tvi = (
            await self._session.execute(
                select(TviScoreOrm)
                .where(TviScoreOrm.village_id == village_id)
                .order_by(desc(TviScoreOrm.calculated_at))
                .limit(1)
            )
        ).scalar_one_or_none()
        return {"pop": pop, "building": building, "transport": transport, "stats": stats, "tvi": tvi}

    async def _latest_pop_and_stats_maps(
        self, village_ids: list[uuid.UUID]
    ) -> tuple[dict[uuid.UUID, SnapPopulationOrm], dict[uuid.UUID, SnapStatisticsOrm]]:
        if not village_ids:
            return {}, {}
        pops = (
            await self._session.execute(
                select(SnapPopulationOrm).where(SnapPopulationOrm.village_id.in_(village_ids))
            )
        ).scalars().all()
        stats_rows = (
            await self._session.execute(
                select(SnapStatisticsOrm).where(SnapStatisticsOrm.village_id.in_(village_ids))
            )
        ).scalars().all()
        pop_map: dict[uuid.UUID, SnapPopulationOrm] = {}
        for pop in pops:
            current = pop_map.get(pop.village_id)
            if current is None or pop.snapshot_date > current.snapshot_date:
                pop_map[pop.village_id] = pop
        stats_map: dict[uuid.UUID, SnapStatisticsOrm] = {}
        for stats in stats_rows:
            current = stats_map.get(stats.village_id)
            if current is None or stats.snapshot_date > current.snapshot_date:
                stats_map[stats.village_id] = stats
        return pop_map, stats_map

    @staticmethod
    def _build_top5_item(village, tvi, region, pop, stats) -> dict:
        pop_change_pct = None
        if pop and pop.net_youth_migration is not None and pop.registered_households:
            pop_change_pct = (pop.net_youth_migration / max(pop.registered_households, 1)) * 100

        vacancy_score = None
        if tvi.vacancy_rate is not None:
            vacancy_score = calculate_vacancy_score(tvi.vacancy_rate) * 100

        return {
            "village_code": village.emd_code,
            "village_name": village.name,
            "sigun_name": region.sigungu,
            "tvi_score": tvi.tvi_score,
            "tvi_grade": tvi.risk_level,
            "annual_pop_change_rate": pop_change_pct,
            "net_youth_migration": pop.net_youth_migration if pop else None,
            "bus_interval_score": tvi.bus_interval_score if tvi.bus_interval_score is not None else 0,
            "vacancy_score": vacancy_score,
            "aging_ratio": stats.aging_ratio if stats else None,
        }
