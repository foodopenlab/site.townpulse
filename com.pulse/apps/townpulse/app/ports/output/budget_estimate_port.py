from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.budget_estimate_entity import BudgetEstimateEntity


class BudgetEstimatePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> BudgetEstimateEntity | None:
        ...
