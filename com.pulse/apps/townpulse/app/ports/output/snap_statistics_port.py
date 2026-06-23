from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.snap_statistics_entity import SnapStatisticsEntity


class SnapStatisticsPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapStatisticsEntity | None:
        ...

    @abstractmethod
    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        ...
