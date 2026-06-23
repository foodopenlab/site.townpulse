from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class TviScoreLatestItemSchema(BaseModel):
    id: str
    village_id: str
    tvi_score: float
    tvi_grade: str
    tvi_label: str
    color_hex: str
    tvi_delta: float | None = None
    risk_level: str
    calculated_at: date
    model_version: str


class TviScoreLatestResponseSchema(BaseModel):
    score: TviScoreLatestItemSchema | None
    found: bool


class TviScoreAllLatestResponseSchema(BaseModel):
    scores: list[TviScoreLatestItemSchema]
    total: int
    danger_count: int
    warning_count: int
    safe_count: int
    avg_tvi_score: float


class TviScoreDangerResponseSchema(BaseModel):
    villages: list[str]
    total: int
