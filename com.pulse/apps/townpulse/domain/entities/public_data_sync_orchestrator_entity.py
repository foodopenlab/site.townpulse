from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class PublicDataSyncOrchestratorEntity:
    id: UUID
    created_at: datetime | None = None
