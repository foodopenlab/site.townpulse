from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(slots=True)
class RegionEntity:
    id: UUID
    sido: str
    sigungu: str
    emd_name: str
    legal_dong_code: str
    sigungu_code: str | None = None
    emd_code: str | None = None
    tago_city_code: str | None = None
    area_km2: float | None = None
    fiscal_self_reliance: float | None = None
    fiscal_data_year: date | None = None
    birth_rate: float | None = None
    daytime_population: float | None = None
    demographic_data_year: date | None = None
