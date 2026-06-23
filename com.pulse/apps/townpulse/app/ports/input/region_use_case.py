from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.region_dto import RegionDto, RegionListResult


class RegionUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> RegionDto | None:
        ...

    @abstractmethod
    async def find_all(self) -> RegionListResult:
        ...

    @abstractmethod
    async def find_by_emd_code(self, emd_code: str) -> RegionDto | None:
        ...
