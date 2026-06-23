from __future__ import annotations

from apps.townpulse.domain.value_objects.tvi_grade_vo import grade_from_score


def clamp_tvi(score: float) -> float:
    return max(0.0, min(100.0, score))


def tvi_with_grade(score: float) -> tuple[float, str]:
    s = clamp_tvi(score)
    return s, grade_from_score(s)
