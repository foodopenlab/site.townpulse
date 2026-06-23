from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class RegionListItemResponse(BaseModel):
    id: str
    sigungu: str
    legal_dong_code: str


class RegionDetailResponse(BaseModel):
    id: str
    sido: str
    sigungu: str
    emd_name: str
    legal_dong_code: str
    emd_code: str | None = None
    sigungu_code: str | None = None
    tago_city_code: str | None = None
    area_km2: float | None = None
    fiscal_self_reliance: float | None = None
    fiscal_data_year: date | None = None
    birth_rate: float | None = None
    daytime_population: float | None = None
    demographic_data_year: date | None = None
