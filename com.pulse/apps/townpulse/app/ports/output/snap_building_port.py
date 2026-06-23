from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.snap_building_entity import SnapBuildingEntity


class SnapBuildingPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapBuildingEntity | None:
        ...

    @abstractmethod
    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        ...
