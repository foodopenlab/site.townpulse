from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.prescription_fund_source_dto import PrescriptionFundSourceDto


class PrescriptionFundSourceUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionFundSourceDto | None:
        ...
