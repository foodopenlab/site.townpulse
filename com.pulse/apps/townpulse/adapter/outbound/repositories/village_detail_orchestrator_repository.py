from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.townpulse.adapter.outbound.orm.models import (
    BudgetEstimateOrm,
    PrescriptionResultOrm,
    PrescriptionTypeOrm,
    SnapBuildingOrm,
    SnapPopulationOrm,
    SnapStatisticsOrm,
    SnapTransportOrm,
    TviScoreOrm,
    VillageOrm,
)
from apps.townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository
from apps.townpulse.adapter.outbound.repositories.tvi_score_repository import TviScoreRepository
from apps.townpulse.app.dtos.prescription_result_dto import PrescriptionItemDto
from apps.townpulse.app.dtos.village_detail_orchestrator_dto import SnapTransportDto, VillageDetailDto
from apps.townpulse.app.ports.output.village_detail_orchestrator_port import VillageDetailOrchestratorPort


class VillageDetailOrchestratorRepository(VillageDetailOrchestratorPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._tvi_repo = TviScoreRepository(session)

    async def fetch_village_detail(self, village_code: str) -> VillageDetailDto | None:
        village_orm = (
            await self._session.execute(
                select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.emd_code == village_code)
            )
        ).scalar_one_or_none()
        if not village_orm:
            return None
        snaps = await self._fetch_latest_snapshots(village_orm.id)
        existing = (
            await self._session.execute(
                select(PrescriptionResultOrm)
                .where(PrescriptionResultOrm.village_id == village_orm.id)
                .order_by(PrescriptionResultOrm.priority_rank, PrescriptionResultOrm.id)
            )
        ).scalars().all()
        preview_raw = await self._prescriptions_to_items(
            PrescriptionResultRepository._dedupe_by_rank(list(existing))[:3]
        ) if existing else []
        detail = self._build_village_detail(village_orm, snaps, preview_raw)
        snap = detail.get("snap_transport")
        return VillageDetailDto(
            village_id=detail["village_id"],
            village_code=detail["village_code"],
            village_name=detail["village_name"],
            sigun_name=detail["sigun_name"],
            tvi_score=detail["tvi_score"],
            tvi_grade=detail["tvi_grade"],
            bus_interval_score=detail["bus_interval_score"],
            vacant_house_rate=detail["vacant_house_rate"],
            elderly_rate=detail["elderly_rate"],
            bus_interval_minutes=detail["bus_interval_minutes"],
            nearest_stop_distance_m=detail["nearest_stop_distance_m"],
            bus_stops_within_1km=detail["bus_stops_within_1km"],
            transport_gap=detail["transport_gap"],
            population_change_rate=detail["population_change_rate"],
            extinction_probability_5y=detail["extinction_probability_5y"],
            snap_transport=SnapTransportDto(**snap) if snap else None,
            updated_at=detail["updated_at"],
            prescriptions_preview=[PrescriptionItemDto(**p) for p in preview_raw],
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
        tvi_entity = await self._tvi_repo.find_latest_by_village(village_id)
        tvi = (
            await self._session.execute(
                select(TviScoreOrm)
                .where(TviScoreOrm.village_id == village_id)
                .order_by(desc(TviScoreOrm.calculated_at))
                .limit(1)
            )
        ).scalar_one_or_none() if tvi_entity else None
        return {"pop": pop, "building": building, "transport": transport, "stats": stats, "tvi": tvi}

    async def _prescriptions_to_items(self, results: list[PrescriptionResultOrm]) -> list[dict]:
        items = []
        for r in results:
            ptype = (
                await self._session.execute(
                    select(PrescriptionTypeOrm).where(PrescriptionTypeOrm.id == r.prescription_type_id)
                )
            ).scalar_one()
            budget = (
                await self._session.execute(
                    select(BudgetEstimateOrm).where(BudgetEstimateOrm.prescription_result_id == r.id)
                )
            ).scalar_one_or_none()
            items.append(
                {
                    "id": str(r.id),
                    "rank": r.priority_rank,
                    "code": ptype.code,
                    "title": ptype.name,
                    "description": r.ai_description,
                    "budget_min": budget.budget_min if budget else 0,
                    "budget_max": budget.budget_max if budget else 0,
                    "tvi_gain_min": r.tvi_gain_min or 0,
                    "tvi_gain_max": r.tvi_gain_max or 0,
                    "fund_applicable": r.fund_applicable,
                    "timeline": ptype.rollout_timeline or "medium",
                }
            )
        return items

    @staticmethod
    def _build_village_detail(village: VillageOrm, snaps: dict, prescriptions: list[dict] | None = None) -> dict:
        tvi = snaps["tvi"]
        pop = snaps["pop"]
        transport = snaps["transport"]
        stats = snaps["stats"]
        bus_score = tvi.bus_interval_score if tvi else 0.0
        transport_gap = bus_score == 0.0 and (transport is None or transport.bus_route_count is not None)
        pop_change = -0.05
        if pop and pop.net_youth_migration and pop.registered_households:
            pop_change = pop.net_youth_migration / max(pop.registered_households, 1)
        sigungu = ""
        if hasattr(village, "region") and village.region:
            sigungu = getattr(village.region, "sigungu", "") or ""
        return {
            "village_id": str(village.id),
            "village_code": village.emd_code,
            "village_name": village.name,
            "sigun_name": sigungu,
            "tvi_score": tvi.tvi_score if tvi else 0,
            "tvi_grade": tvi.risk_level if tvi else "safe",
            "bus_interval_score": bus_score,
            "vacant_house_rate": tvi.vacancy_rate if tvi else 0,
            "elderly_rate": stats.aging_ratio if stats else 0,
            "bus_interval_minutes": transport.avg_bus_interval_min if transport else None,
            "nearest_stop_distance_m": transport.nearest_stop_distance_m if transport else None,
            "bus_stops_within_1km": transport.bus_stops_within_1km if transport else None,
            "transport_gap": transport_gap,
            "population_change_rate": pop_change,
            "extinction_probability_5y": min(0.95, max(0.05, (100 - (tvi.tvi_score if tvi else 50)) / 100)),
            "snap_transport": {
                "bus_route_count": transport.bus_route_count if transport else None,
                "avg_bus_interval_min": transport.avg_bus_interval_min if transport else None,
                "nearest_stop_distance_m": transport.nearest_stop_distance_m if transport else None,
                "bus_stops_within_1km": transport.bus_stops_within_1km if transport else None,
                "fetched_at": (
                    transport.fetched_at.isoformat()
                    if transport and transport.fetched_at
                    else datetime.utcnow().isoformat()
                ),
            }
            if transport
            else None,
            "updated_at": datetime.utcnow().isoformat(),
            "prescriptions_preview": prescriptions or [],
        }
