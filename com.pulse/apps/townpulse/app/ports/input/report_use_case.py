from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.report_dto import ReportDto


class ReportUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> ReportDto | None:
        ...
