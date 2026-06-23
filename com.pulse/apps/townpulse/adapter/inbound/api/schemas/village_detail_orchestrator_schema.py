from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from apps.townpulse.adapter.inbound.api.schemas.prescription_result_schema import PrescriptionItemResponse


class SnapTransportResponse(BaseModel):
    bus_route_count: int | None
    avg_bus_interval_min: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    fetched_at: str


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
