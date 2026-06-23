from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True)
class PrescriptionItemDto:
    id: str
    rank: int
    code: str
    title: str
    description: str | None
    budget_min: int
    budget_max: int
    tvi_gain_min: float
    tvi_gain_max: float
    fund_applicable: bool
    timeline: str


@dataclass(slots=True)
class PrescriptionListDto:
    village_id: str
    prescriptions: list[PrescriptionItemDto] = field(default_factory=list)
    generated_at: str = ""


@dataclass(slots=True)
class PrescriptionResultGenerateCommand:
    village_id: UUID


@dataclass(slots=True)
class PrescriptionResultGenerateResult:
    results: list[PrescriptionItemDto]
    total: int


@dataclass(slots=True)
class PrescriptionResultStreamCommand:
    prescription_result_id: UUID


@dataclass(slots=True)
class PrescriptionResultQueryByVillage:
    village_id: UUID


@dataclass(slots=True)
class PrescriptionResultListResult:
    village_id: str
    prescriptions: list[PrescriptionItemDto] = field(default_factory=list)
    generated_at: str = ""
