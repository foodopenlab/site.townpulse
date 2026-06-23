from __future__ import annotations

from pydantic import BaseModel


class PrescriptionTypeListItemResponse(BaseModel):
    code: str
    name: str
    category: str | None = None


class PrescriptionTypeDetailResponse(BaseModel):
    id: str
    code: str
    name: str
    category: str | None = None
    rollout_timeline: str | None = None
    is_active: bool = True
