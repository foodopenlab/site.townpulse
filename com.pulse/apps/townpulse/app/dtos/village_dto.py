from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class VillageDto:
    id: UUID
    emd_code: str
    name: str
    region_id: UUID | None = None
    lat: float | None = None
    lng: float | None = None
    last_synced_at: datetime | None = None
    sigungu: str | None = None


@dataclass(slots=True)
class VillageListResult:
    items: list[VillageDto]
    total: int
