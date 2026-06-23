from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.snap_statistics_dto import SnapStatisticsDto


class SnapStatisticsUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapStatisticsDto | None:
        ...
