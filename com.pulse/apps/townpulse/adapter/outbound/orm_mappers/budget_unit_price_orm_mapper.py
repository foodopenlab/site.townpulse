from __future__ import annotations

from apps.townpulse.domain.entities.budget_unit_price_entity import BudgetUnitPriceEntity


class BudgetUnitPriceOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> BudgetUnitPriceEntity:
        return BudgetUnitPriceEntity(id=orm_obj.id)
