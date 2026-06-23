from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.dispatch_rule_port import DispatchRulePort
from apps.townpulse.domain.entities.dispatch_rule_entity import DispatchRuleEntity


class DispatchRuleRepository(DispatchRulePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> DispatchRuleEntity | None:
        return None
