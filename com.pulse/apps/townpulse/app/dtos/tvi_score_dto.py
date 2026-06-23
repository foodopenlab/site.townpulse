from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(slots=True)
class TviScoreLatestQuery:
    village_id: UUID


@dataclass(slots=True)
class TviScoreLatestItem:
    id: UUID
    village_id: UUID
    tvi_score: float
    tvi_grade: str
    tvi_label: str
    color_hex: str
    tvi_delta: float | None
    risk_level: str
    calculated_at: date
    model_version: str


@dataclass(slots=True)
class TviScoreLatestResult:
    score: TviScoreLatestItem | None
    found: bool


@dataclass(slots=True)
class TviScoreAllLatestQuery:
    grade_filter: str | None = None
    sigun_filter: str | None = None


@dataclass(slots=True)
class TviScoreAllLatestResult:
    scores: list[TviScoreLatestItem]
    total: int
    danger_count: int
    warning_count: int
    safe_count: int
    avg_tvi_score: float


@dataclass(slots=True)
class TviScoreDangerQuery:
    threshold: float = 30.0


@dataclass(slots=True)
class TviScoreDangerResult:
    villages: list[UUID]
    total: int
