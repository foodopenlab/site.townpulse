from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.subscription_dto import SubscriptionDto


class SubscriptionUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SubscriptionDto | None:
        ...
