from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.dispatch_rule_schema import DispatchRuleResponse
from apps.townpulse.app.dtos.dispatch_rule_dto import DispatchRuleDto


class DispatchRuleMapper:
    @staticmethod
    def to_response(dto: DispatchRuleDto) -> DispatchRuleResponse:
        return DispatchRuleResponse(id=str(dto.id))
