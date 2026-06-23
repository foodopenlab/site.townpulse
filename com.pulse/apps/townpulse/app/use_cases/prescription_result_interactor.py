from __future__ import annotations

from collections.abc import AsyncGenerator

from apps.townpulse.app.dtos.prescription_result_dto import (
    PrescriptionResultGenerateCommand,
    PrescriptionResultGenerateResult,
    PrescriptionResultListResult,
    PrescriptionResultQueryByVillage,
    PrescriptionResultStreamCommand,
)
from apps.townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from apps.townpulse.app.ports.output.budget_estimate_port import BudgetEstimatePort
from apps.townpulse.app.ports.output.dispatch_rule_port import DispatchRulePort
from apps.townpulse.app.ports.output.prescription_fund_source_port import PrescriptionFundSourcePort
from apps.townpulse.app.ports.output.prescription_result_port import PrescriptionResultPort
from apps.townpulse.app.ports.output.prescription_type_port import PrescriptionTypePort
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.app.ports.output.village_port import VillagePort


class PrescriptionResultInteractor(PrescriptionResultUseCase):
    def __init__(
        self,
        result_repo: PrescriptionResultPort,
        dispatch_repo: DispatchRulePort,
        village_repo: VillagePort,
        tvi_score_repo: TviScorePort,
        prescription_type_repo: PrescriptionTypePort,
        fund_source_repo: PrescriptionFundSourcePort,
        budget_estimate_repo: BudgetEstimatePort,
    ) -> None:
        self._result_repo = result_repo
        self._dispatch_repo = dispatch_repo
        self._village_repo = village_repo
        self._tvi_score_repo = tvi_score_repo
        self._prescription_type_repo = prescription_type_repo
        self._fund_source_repo = fund_source_repo
        self._budget_estimate_repo = budget_estimate_repo

    async def generate_for_village(
        self, command: PrescriptionResultGenerateCommand
    ) -> PrescriptionResultGenerateResult:
        village = await self._village_repo.find_by_id(command.village_id)
        if village is None:
            raise ValueError("마을을 찾을 수 없습니다.")
        tvi = await self._tvi_score_repo.find_latest_by_village(command.village_id)
        if tvi is None:
            raise ValueError("TVI 데이터가 없습니다.")
        items = await self._result_repo.generate_for_village(command.village_id)
        return PrescriptionResultGenerateResult(results=items, total=len(items))

    async def find_by_village(self, query: PrescriptionResultQueryByVillage) -> PrescriptionResultListResult:
        dto = await self._result_repo.find_by_village(query.village_id)
        return PrescriptionResultListResult(
            village_id=dto.village_id,
            prescriptions=dto.prescriptions,
            generated_at=dto.generated_at,
        )

    async def stream_ai_description(self, command: PrescriptionResultStreamCommand) -> AsyncGenerator[str, None]:
        async for chunk in self._result_repo.stream_ai_description(command.prescription_result_id):
            yield chunk
