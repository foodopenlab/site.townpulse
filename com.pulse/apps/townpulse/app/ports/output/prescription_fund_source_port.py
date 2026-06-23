from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.prescription_fund_source_entity import PrescriptionFundSourceEntity


class PrescriptionFundSourcePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> PrescriptionFundSourceEntity | None:
        ...
