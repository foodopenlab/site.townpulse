from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class VillageSnapshotVo:
    population_total: int | None
    residential_buildings: int | None
    bus_route_count: int | None
    avg_bus_interval_min: float | None
    nearest_stop_distance_m: int | None
    bus_stops_within_1km: int | None
    aging_ratio: float | None
    fetched_at: datetime | None = None
