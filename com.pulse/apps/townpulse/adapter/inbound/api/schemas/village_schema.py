from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class VillageListItemResponse(BaseModel):
    id: str
    emd_code: str
    name: str


class VillageDetailResponse(BaseModel):
    id: str
    emd_code: str
    name: str
    region_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    last_synced_at: datetime | None = None
    sigungu: str | None = None
