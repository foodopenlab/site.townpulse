from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.snap_population_entity import SnapPopulationEntity


class SnapPopulationPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapPopulationEntity | None:
        ...

    @abstractmethod
    async def ingest_core_from_public_api(self, legal_dong_code: str) -> None:
        ...

    @abstractmethod
    async def ingest_migration_from_public_api(self, legal_dong_code: str) -> None:
        ...

    @abstractmethod
    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        ...
