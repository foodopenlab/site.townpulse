from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.prescription_type_entity import PrescriptionTypeEntity


class PrescriptionTypePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionTypeEntity | None:
        ...

    @abstractmethod
    async def find_all_active(self) -> list[PrescriptionTypeEntity]:
        ...

    @abstractmethod
    async def find_by_code(self, code: str) -> PrescriptionTypeEntity | None:
        ...
