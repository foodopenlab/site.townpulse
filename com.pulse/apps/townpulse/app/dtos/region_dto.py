from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(slots=True)
class RegionDto:
    id: UUID
    sigungu: str
    legal_dong_code: str
    sido: str | None = None
    emd_name: str | None = None
    emd_code: str | None = None
    sigungu_code: str | None = None
    tago_city_code: str | None = None
    area_km2: float | None = None
    fiscal_self_reliance: float | None = None
    fiscal_data_year: date | None = None
    birth_rate: float | None = None
    daytime_population: float | None = None
    demographic_data_year: date | None = None


@dataclass(slots=True)
class RegionListResult:
    items: list[RegionDto]
    total: int
