from __future__ import annotations

from apps.townpulse.domain.entities.dispatch_rule_entity import DispatchRuleEntity


class DispatchRuleOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> DispatchRuleEntity:
        return DispatchRuleEntity(id=orm_obj.id)
