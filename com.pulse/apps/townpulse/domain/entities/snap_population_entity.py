from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class SnapPopulationEntity:
    id: UUID
    created_at: datetime | None = None
