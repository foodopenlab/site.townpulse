from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.dispatch_rule_entity import DispatchRuleEntity


class DispatchRulePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> DispatchRuleEntity | None:
        ...
