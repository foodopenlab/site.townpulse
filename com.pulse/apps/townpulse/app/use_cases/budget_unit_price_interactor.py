from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.budget_unit_price_dto import BudgetUnitPriceDto
from apps.townpulse.app.ports.input.budget_unit_price_use_case import BudgetUnitPriceUseCase
from apps.townpulse.app.ports.output.budget_unit_price_port import BudgetUnitPricePort


class BudgetUnitPriceInteractor(BudgetUnitPriceUseCase):
    def __init__(self, port: BudgetUnitPricePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> BudgetUnitPriceDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return BudgetUnitPriceDto(id=entity.id)
