from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class PrescriptionTypeEntity:
    id: UUID
    code: str
    name: str
    category: str | None = None
    rollout_timeline: str | None = None
    is_active: bool = True
