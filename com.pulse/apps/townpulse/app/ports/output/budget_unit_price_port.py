from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.budget_unit_price_entity import BudgetUnitPriceEntity


class BudgetUnitPricePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> BudgetUnitPriceEntity | None:
        ...
