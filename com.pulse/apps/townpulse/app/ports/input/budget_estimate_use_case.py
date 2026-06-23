from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.budget_estimate_dto import BudgetEstimateDto


class BudgetEstimateUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> BudgetEstimateDto | None:
        ...
