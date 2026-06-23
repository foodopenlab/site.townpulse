from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.budget_unit_price_schema import BudgetUnitPriceResponse
from apps.townpulse.app.dtos.budget_unit_price_dto import BudgetUnitPriceDto


class BudgetUnitPriceMapper:
    @staticmethod
    def to_response(dto: BudgetUnitPriceDto) -> BudgetUnitPriceResponse:
        return BudgetUnitPriceResponse(id=str(dto.id))
