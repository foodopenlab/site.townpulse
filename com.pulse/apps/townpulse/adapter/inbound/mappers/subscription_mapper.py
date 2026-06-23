from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.subscription_schema import SubscriptionResponse
from apps.townpulse.app.dtos.subscription_dto import SubscriptionDto


class SubscriptionMapper:
    @staticmethod
    def to_response(dto: SubscriptionDto) -> SubscriptionResponse:
        return SubscriptionResponse(id=str(dto.id))
