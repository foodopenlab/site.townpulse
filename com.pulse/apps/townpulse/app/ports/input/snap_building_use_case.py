from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.snap_building_dto import SnapBuildingDto


class SnapBuildingUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapBuildingDto | None:
        ...
