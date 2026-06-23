from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import (
    BudgetEstimateOrm,
    BudgetUnitPriceOrm,
    DispatchRuleOrm,
    PrescriptionResultOrm,
    PrescriptionTypeOrm,
    SnapBuildingOrm,
    SnapPopulationOrm,
    SnapStatisticsOrm,
    SnapTransportOrm,
    TviScoreOrm,
    VillageOrm,
)
from apps.townpulse.app.dtos.prescription_result_dto import PrescriptionItemDto, PrescriptionListDto
from apps.townpulse.app.ports.output.prescription_result_port import PrescriptionResultPort
from apps.townpulse.services.tvi_calculator import simulate_tvi_gain
from core.matrix.grid_keymaker_secret_manager import TOWNPULSE_PRESCRIPTION_PERSONA
from core.matrix.grid_smith_agent_scaler import get_smith


class PrescriptionResultRepository(PrescriptionResultPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _dedupe_by_rank(results: list[PrescriptionResultOrm]) -> list[PrescriptionResultOrm]:
        seen: set[int] = set()
        unique: list[PrescriptionResultOrm] = []
        for result in results:
            if result.priority_rank in seen:
                continue
            seen.add(result.priority_rank)
            unique.append(result)
        return unique

    async def generate_for_village(self, village_id: UUID) -> list[PrescriptionItemDto]:
        results = await self._generate_prescriptions(village_id)
        items = await self._prescriptions_to_items(results)
        return [PrescriptionItemDto(**item) for item in items]  # type: ignore[arg-type]

    async def find_by_village(self, village_id: UUID) -> PrescriptionListDto:
        results = (
            await self._session.execute(
                select(PrescriptionResultOrm)
                .where(PrescriptionResultOrm.village_id == village_id)
                .order_by(PrescriptionResultOrm.priority_rank, PrescriptionResultOrm.id)
            )
        ).scalars().all()
        deduped = self._dedupe_by_rank(list(results))
        items = await self._prescriptions_to_items(deduped)
        return PrescriptionListDto(
            village_id=str(village_id),
            prescriptions=[PrescriptionItemDto(**item) for item in items],  # type: ignore[arg-type]
            generated_at=datetime.utcnow().isoformat(),
        )

    async def stream_ai_description(self, prescription_id: UUID) -> AsyncGenerator[str, None]:
        result = (
            await self._session.execute(
                select(PrescriptionResultOrm).where(PrescriptionResultOrm.id == prescription_id)
            )
        ).scalar_one_or_none()
        if not result:
            raise ValueError("처방을 찾을 수 없습니다.")
        village = (
            await self._session.execute(select(VillageOrm).where(VillageOrm.id == result.village_id))
        ).scalar_one()
        tvi = (
            await self._session.execute(select(TviScoreOrm).where(TviScoreOrm.id == result.tvi_score_id))
        ).scalar_one()
        prompt = f"""{TOWNPULSE_PRESCRIPTION_PERSONA}

[데이터]
village_name: {village.name}
tvi_score: {tvi.tvi_score}
risk_level: {tvi.risk_level}
priority_rank: {result.priority_rank}
tvi_gain_min: {result.tvi_gain_min}
tvi_gain_max: {result.tvi_gain_max}
fund_applicable: {result.fund_applicable}
"""
        async for chunk in get_smith().stream_text(prompt):
            yield chunk

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

    async def _generate_prescriptions(self, village_id: uuid.UUID) -> list[PrescriptionResultOrm]:
        village = (
            await self._session.execute(
                select(VillageOrm).where(VillageOrm.id == village_id).with_for_update()
            )
        ).scalar_one_or_none()
        if not village:
            raise ValueError("마을을 찾을 수 없습니다.")
        snaps = await self._fetch_latest_snapshots(village_id)
        tvi = snaps["tvi"]
        if not tvi:
            raise ValueError("TVI 데이터가 없습니다.")

        existing = (
            await self._session.execute(
                select(PrescriptionResultOrm)
                .where(PrescriptionResultOrm.village_id == village_id)
                .order_by(PrescriptionResultOrm.priority_rank, PrescriptionResultOrm.id)
            )
        ).scalars().all()
        if existing:
            return self._dedupe_by_rank(list(existing))

        rules = (
            await self._session.execute(select(DispatchRuleOrm).order_by(DispatchRuleOrm.priority_rank))
        ).scalars().all()
        types = {t.id: t for t in (await self._session.execute(select(PrescriptionTypeOrm))).scalars().all()}
        prices = (await self._session.execute(select(BudgetUnitPriceOrm))).scalars().all()
        price_by_type = {p.prescription_type_id: p for p in prices}

        results: list[PrescriptionResultOrm] = []
        for rule in rules[:3]:
            ptype = types[rule.prescription_type_id]
            gain_min, gain_max = simulate_tvi_gain(
                ptype.code, tvi.tvi_score, tvi.vacancy_rate or 0, tvi.bus_interval_score or 0
            )
            result = PrescriptionResultOrm(
                id=uuid.uuid4(),
                village_id=village_id,
                tvi_score_id=tvi.id,
                prescription_type_id=ptype.id,
                priority_rank=rule.priority_rank,
                tvi_gain_min=gain_min,
                tvi_gain_max=gain_max,
                fund_applicable=True,
            )
            self._session.add(result)
            await self._session.flush()
            price = price_by_type.get(ptype.id)
            if price:
                self._session.add(
                    BudgetEstimateOrm(
                        id=uuid.uuid4(),
                        prescription_result_id=result.id,
                        budget_unit_price_id=price.id,
                        quantity=1,
                        budget_min=price.price_min,
                        budget_max=price.price_max,
                        calculation_note="MVP 시드 단가",
                    )
                )
            results.append(result)
        return results

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
