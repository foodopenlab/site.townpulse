from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.prescription_type_dto import PrescriptionTypeDto, PrescriptionTypeListResult


class PrescriptionTypeUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionTypeDto | None:
        ...

    @abstractmethod
    async def find_all_active(self) -> PrescriptionTypeListResult:
        ...

    @abstractmethod
    async def find_by_code(self, code: str) -> PrescriptionTypeDto | None:
        ...
