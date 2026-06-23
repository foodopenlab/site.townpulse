from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReportBuildQueryDto:
    include_risk_analysis: bool = True
    include_prescriptions: bool = True
    include_budget: bool = True
    include_map_snapshot: bool = False


@dataclass(slots=True)
class ReportDataDto:
    village_code: str
    village_name: str
    sigun_name: str
    tvi_score: float
    tvi_grade: str
    generated_at: str
    sections: dict
