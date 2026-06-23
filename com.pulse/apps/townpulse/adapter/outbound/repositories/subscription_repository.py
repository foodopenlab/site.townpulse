from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.subscription_port import SubscriptionPort
from apps.townpulse.domain.entities.subscription_entity import SubscriptionEntity


class SubscriptionRepository(SubscriptionPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> SubscriptionEntity | None:
        return None
