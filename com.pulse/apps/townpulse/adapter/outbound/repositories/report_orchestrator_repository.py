from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.townpulse.adapter.outbound.orm.models import (
    ReportOrm,
    SnapBuildingOrm,
    SnapPopulationOrm,
    SnapStatisticsOrm,
    SnapTransportOrm,
    TviScoreOrm,
    VillageOrm,
)
from apps.townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository
from apps.townpulse.adapter.outbound.repositories.tvi_score_repository import TviScoreRepository
from apps.townpulse.adapter.outbound.repositories.village_repository import VillageRepository
from apps.townpulse.app.dtos.report_orchestrator_dto import ReportBuildQueryDto, ReportDataDto
from apps.townpulse.app.ports.output.report_orchestrator_port import ReportOrchestratorPort
from core.matrix.grid_trinity_hacker_mixin import DEMO_SCOPE


class ReportOrchestratorRepository(ReportOrchestratorPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._village_repo = VillageRepository(session)
        self._tvi_repo = TviScoreRepository(session)

    async def build_report_data(
        self, village_code: str, query: ReportBuildQueryDto, user_claims: dict
    ) -> ReportDataDto | None:
        village_entity = await self._village_repo.find_by_code(village_code)
        if not village_entity:
            return None
        village = (
            await self._session.execute(
                select(VillageOrm).options(selectinload(VillageOrm.region)).where(VillageOrm.id == village_entity.id)
            )
        ).scalar_one()
        snaps = await self._fetch_latest_snapshots(village.id)
        tvi = snaps["tvi"]
        if not tvi:
            return None
        user_sub = user_claims.get("sub", "demo-guest")
        if user_claims.get("scope") != DEMO_SCOPE:
            self._session.add(
                ReportOrm(
                    id=uuid.uuid4(),
                    user_id=uuid.UUID(user_sub) if user_sub != "demo-guest" else uuid.uuid4(),
                    village_id=village.id,
                    tvi_score_id=tvi.id,
                    title=f"{village.name} 마을생존 리포트",
                    format="pdf",
                )
            )
        detail = self._build_village_detail(village, snaps)
        prescriptions_section = None
        budget_section = None
        if query.include_prescriptions or query.include_budget:
            prescription_repo = PrescriptionResultRepository(self._session)
            prescription_dto = await prescription_repo.find_by_village(village.id)
            if not prescription_dto.prescriptions:
                try:
                    await prescription_repo.generate_for_village(village.id)
                    prescription_dto = await prescription_repo.find_by_village(village.id)
                except ValueError:
                    prescription_dto = None
            if prescription_dto and prescription_dto.prescriptions:
                unique_prescriptions = []
                seen_ranks: set[int] = set()
                for p in prescription_dto.prescriptions:
                    if p.rank in seen_ranks:
                        continue
                    seen_ranks.add(p.rank)
                    unique_prescriptions.append(p)
                items = [
                    {
                        "id": p.id,
                        "rank": p.rank,
                        "code": p.code,
                        "title": p.title,
                        "tvi_gain_min": p.tvi_gain_min,
                        "tvi_gain_max": p.tvi_gain_max,
                        "budget_min": p.budget_min,
                        "budget_max": p.budget_max,
                        "timeline": p.timeline,
                        "fund_applicable": p.fund_applicable,
                    }
                    for p in unique_prescriptions
                ]
                if query.include_prescriptions:
                    prescriptions_section = items
                if query.include_budget:
                    budget_section = {
                        "total_min_manwon": sum(i["budget_min"] for i in items),
                        "total_max_manwon": sum(i["budget_max"] for i in items),
                        "currency_note": "만원 단위",
                        "items": [
                            {
                                "rank": i["rank"],
                                "title": i["title"],
                                "budget_min": i["budget_min"],
                                "budget_max": i["budget_max"],
                            }
                            for i in items
                        ],
                    }
        return ReportDataDto(
            village_code=village.emd_code,
            village_name=village.name,
            sigun_name=detail["sigun_name"],
            tvi_score=detail["tvi_score"],
            tvi_grade=detail["tvi_grade"],
            generated_at=datetime.utcnow().isoformat(),
            sections={
                "risk_analysis": detail if query.include_risk_analysis else None,
                "prescriptions": prescriptions_section,
                "budget": budget_section,
            },
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

    @staticmethod
    def _build_village_detail(village: VillageOrm, snaps: dict) -> dict:
        tvi = snaps["tvi"]
        pop = snaps["pop"]
        transport = snaps["transport"]
        stats = snaps["stats"]
        bus_score = tvi.bus_interval_score if tvi else 0.0
        transport_gap = bus_score == 0.0 and (transport is None or transport.bus_route_count is not None)
        pop_change = -0.05
        if pop and pop.net_youth_migration and pop.registered_households:
            pop_change = pop.net_youth_migration / max(pop.registered_households, 1)
        return {
            "village_id": str(village.id),
            "village_code": village.emd_code,
            "village_name": village.name,
            "sigun_name": village.region.sigungu if village.region else "",
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
            "updated_at": datetime.utcnow().isoformat(),
        }
