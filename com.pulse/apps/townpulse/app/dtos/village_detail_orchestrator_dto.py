from __future__ import annotations

from dataclasses import dataclass, field

from apps.townpulse.app.dtos.prescription_result_dto import PrescriptionItemDto


@dataclass(slots=True)
class SnapTransportDto:
    bus_route_count: int | None
    avg_bus_interval_min: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    fetched_at: str


@dataclass(slots=True)
class VillageDetailDto:
    village_id: str
    village_code: str
    village_name: str
    sigun_name: str
    tvi_score: float
    tvi_grade: str
    bus_interval_score: float
    vacant_house_rate: float
    elderly_rate: float
    bus_interval_minutes: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    transport_gap: bool
    population_change_rate: float
    extinction_probability_5y: float
    snap_transport: SnapTransportDto | None
    updated_at: str
    prescriptions_preview: list[PrescriptionItemDto] = field(default_factory=list)
