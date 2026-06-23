from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.budget_estimate_schema import BudgetEstimateResponse
from apps.townpulse.app.dtos.budget_estimate_dto import BudgetEstimateDto


class BudgetEstimateMapper:
    @staticmethod
    def to_response(dto: BudgetEstimateDto) -> BudgetEstimateResponse:
        return BudgetEstimateResponse(id=str(dto.id))
