from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.budget_unit_price_port import BudgetUnitPricePort
from apps.townpulse.domain.entities.budget_unit_price_entity import BudgetUnitPriceEntity


class BudgetUnitPriceRepository(BudgetUnitPricePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> BudgetUnitPriceEntity | None:
        return None
