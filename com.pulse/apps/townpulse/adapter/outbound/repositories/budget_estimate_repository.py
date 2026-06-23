from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.budget_estimate_port import BudgetEstimatePort
from apps.townpulse.domain.entities.budget_estimate_entity import BudgetEstimateEntity


class BudgetEstimateRepository(BudgetEstimatePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> BudgetEstimateEntity | None:
        return None
