from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


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
    annual_pop_change_rate: float | None = None
    net_youth_migration: int | None = None
    vacancy_score: float | None = None
    aging_ratio: float | None = None


class VillageMapSummaryResponse(BaseModel):
    village_code: str
    village_name: str
    tvi_score: float
    tvi_grade: Literal["danger", "warning", "safe"]
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
