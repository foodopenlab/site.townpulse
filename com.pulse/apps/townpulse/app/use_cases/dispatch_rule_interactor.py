from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.dispatch_rule_dto import DispatchRuleDto
from apps.townpulse.app.ports.input.dispatch_rule_use_case import DispatchRuleUseCase
from apps.townpulse.app.ports.output.dispatch_rule_port import DispatchRulePort


class DispatchRuleInteractor(DispatchRuleUseCase):
    def __init__(self, port: DispatchRulePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> DispatchRuleDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return DispatchRuleDto(id=entity.id)
