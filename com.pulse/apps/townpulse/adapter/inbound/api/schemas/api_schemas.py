from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    org_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    org_name: str
    user_name: str


class DemoTokenResponse(BaseModel):
    access_token: str
    scope: str
    expires_in: int


class UserMeResponse(BaseModel):
    user_id: str
    org_id: str
    user_name: str
    role: str


class DashboardSummaryResponse(BaseModel):
    total_villages: int
    danger_count: int
    warning_count: int
    safe_count: int
    total_vacant_houses: int
    transport_gap_count: int
    top5_danger_villages: list[dict]
    grade_changed_this_month: int = 0
    pending_prescription_count: int = 0


class VillageListItemResponse(BaseModel):
    village_id: str
    village_code: str
    village_name: str
    sigun_name: str
    tvi_score: float
    tvi_grade: Literal["danger", "warning", "safe"]
    tvi_label: str
    color_hex: str
    lat: float
    lng: float
    bus_interval_score: float | None = None
    nearest_stop_distance_m: int | None = None


class VillageMapSummaryResponse(BaseModel):
    village_code: str
    village_name: str
    tvi_score: float
    tvi_grade: Literal["danger", "warning", "safe"]
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None


class SnapTransportResponse(BaseModel):
    bus_route_count: int | None
    avg_bus_interval_min: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    fetched_at: str


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


class VillageDetailResponse(BaseModel):
    village_id: str
    village_code: str
    village_name: str
    sigun_name: str
    tvi_score: float
    tvi_grade: Literal["danger", "warning", "safe"]
    bus_interval_score: float
    vacant_house_rate: float
    elderly_rate: float
    bus_interval_minutes: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    transport_gap: bool
    population_change_rate: float
    extinction_probability_5y: float
    snap_transport: SnapTransportResponse | None = None
    updated_at: str
    prescriptions_preview: list[PrescriptionItemResponse] = Field(default_factory=list)


class PrescriptionCreateRequest(BaseModel):
    village_id: str


class PrescriptionListResponse(BaseModel):
    village_id: str
    prescriptions: list[PrescriptionItemResponse]
    generated_at: str


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
