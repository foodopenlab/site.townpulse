from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.budget_unit_price_dto import BudgetUnitPriceDto


class BudgetUnitPriceUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> BudgetUnitPriceDto | None:
        ...
