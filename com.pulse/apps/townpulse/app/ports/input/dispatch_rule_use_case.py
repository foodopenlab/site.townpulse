from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.dispatch_rule_dto import DispatchRuleDto


class DispatchRuleUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> DispatchRuleDto | None:
        ...
