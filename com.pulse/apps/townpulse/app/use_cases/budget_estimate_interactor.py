from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.budget_estimate_dto import BudgetEstimateDto
from apps.townpulse.app.ports.input.budget_estimate_use_case import BudgetEstimateUseCase
from apps.townpulse.app.ports.output.budget_estimate_port import BudgetEstimatePort


class BudgetEstimateInteractor(BudgetEstimateUseCase):
    def __init__(self, port: BudgetEstimatePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> BudgetEstimateDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return BudgetEstimateDto(id=entity.id)
