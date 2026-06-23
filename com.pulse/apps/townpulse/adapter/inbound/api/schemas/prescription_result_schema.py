from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class PrescriptionItemResponse(BaseModel):
    id: str
    rank: Literal[1, 2, 3]
    code: str
    title: str
    description: str | None
    budget_min: int
    budget_max: int
    tvi_gain_min: float
    tvi_gain_max: float
    fund_applicable: bool
    timeline: Literal["urgent", "medium", "long"]


class PrescriptionCreateRequest(BaseModel):
    village_id: str


class PrescriptionGenerateResponse(BaseModel):
    prescriptions: list[PrescriptionItemResponse]
    total: int


class PrescriptionListResponse(BaseModel):
    village_id: str
    prescriptions: list[PrescriptionItemResponse]
    generated_at: str
