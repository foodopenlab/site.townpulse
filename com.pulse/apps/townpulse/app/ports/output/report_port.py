from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.report_entity import ReportEntity


class ReportPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> ReportEntity | None:
        ...
