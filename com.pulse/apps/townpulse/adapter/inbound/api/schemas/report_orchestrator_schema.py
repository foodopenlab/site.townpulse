from __future__ import annotations

from pydantic import BaseModel


class ReportBuildRequest(BaseModel):
    include_risk_analysis: bool = True
    include_prescriptions: bool = True
    include_budget: bool = True
    include_map_snapshot: bool = False


class ReportDataResponse(BaseModel):
    village_code: str
    village_name: str
    sigun_name: str
    tvi_score: float
    tvi_grade: str
    generated_at: str
    sections: dict
