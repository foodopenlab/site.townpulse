from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from apps.townpulse.domain.value_objects.tvi_grade_vo import TviGradeVO


@dataclass(slots=True)
class TviScoreEntity:
    id: UUID
    village_id: UUID
    calculated_at: date
    tvi_score: float
    risk_level: str
    pop_decline_score: float | None = None
    vacancy_rate: float | None = None
    bus_interval_score: float | None = None
    prev_tvi_score: float | None = None
    tvi_delta: float | None = None
    model_version: str = "weighted_sum_v1"

    @property
    def tvi_grade(self) -> TviGradeVO:
        return TviGradeVO.from_risk_level(self.risk_level)
