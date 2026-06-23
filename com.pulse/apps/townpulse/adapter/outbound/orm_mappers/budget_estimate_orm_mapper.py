from __future__ import annotations

from apps.townpulse.domain.entities.budget_estimate_entity import BudgetEstimateEntity


class BudgetEstimateOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> BudgetEstimateEntity:
        return BudgetEstimateEntity(id=orm_obj.id)
