from __future__ import annotations

from apps.townpulse.domain.entities.subscription_entity import SubscriptionEntity


class SubscriptionOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> SubscriptionEntity:
        return SubscriptionEntity(id=orm_obj.id)
