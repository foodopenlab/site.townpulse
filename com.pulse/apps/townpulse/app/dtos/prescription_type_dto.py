from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class PrescriptionTypeDto:
    id: UUID
    code: str
    name: str
    category: str | None = None
    rollout_timeline: str | None = None
    is_active: bool = True


@dataclass(slots=True)
class PrescriptionTypeListResult:
    items: list[PrescriptionTypeDto]
    total: int
