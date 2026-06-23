from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.prescription_indicator_dto import PrescriptionIndicatorDto


class PrescriptionIndicatorUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionIndicatorDto | None:
        ...
