from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.subscription_dto import SubscriptionDto
from apps.townpulse.app.ports.input.subscription_use_case import SubscriptionUseCase
from apps.townpulse.app.ports.output.subscription_port import SubscriptionPort


class SubscriptionInteractor(SubscriptionUseCase):
    def __init__(self, port: SubscriptionPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> SubscriptionDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return SubscriptionDto(id=entity.id)
