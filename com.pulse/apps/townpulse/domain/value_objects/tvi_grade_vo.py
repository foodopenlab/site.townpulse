from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TviGrade = Literal["danger", "warning", "safe"]

GRADE_COLORS: dict[str, str] = {"danger": "#E74C3C", "warning": "#F39C12", "safe": "#27AE60"}
GRADE_LABELS: dict[str, str] = {"danger": "소멸위험", "warning": "주의", "safe": "양호"}


def grade_from_score(score: float) -> TviGrade:
    if score < 30:
        return "danger"
    if score < 60:
        return "warning"
    return "safe"


@dataclass(frozen=True, slots=True)
class TviGradeVO:
    grade: TviGrade
    label: str
    color_hex: str

    @classmethod
    def from_score(cls, score: float) -> TviGradeVO:
        g = grade_from_score(score)
        return cls(grade=g, label=GRADE_LABELS[g], color_hex=GRADE_COLORS[g])

    @classmethod
    def from_risk_level(cls, risk_level: str) -> TviGradeVO:
        g: TviGrade = risk_level if risk_level in ("danger", "warning", "safe") else "safe"
        return cls(grade=g, label=GRADE_LABELS.get(g, risk_level), color_hex=GRADE_COLORS.get(g, "#999"))
