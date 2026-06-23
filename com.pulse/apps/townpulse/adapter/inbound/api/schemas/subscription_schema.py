from __future__ import annotations

from pydantic import BaseModel


class SubscriptionResponse(BaseModel):
    id: str
