from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class VillageEntity:
    id: UUID
    region_id: UUID
    name: str
    emd_code: str
    lat: float | None = None
    lng: float | None = None
    last_synced_at: datetime | None = None
    sigungu: str | None = None
    sigungu_code: str | None = None

