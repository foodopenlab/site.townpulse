from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.subscription_entity import SubscriptionEntity


class SubscriptionPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SubscriptionEntity | None:
        ...
