from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.prescription_indicator_entity import PrescriptionIndicatorEntity


class PrescriptionIndicatorPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionIndicatorEntity | None:
        ...
