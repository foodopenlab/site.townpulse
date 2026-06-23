from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.village_dto import VillageDto, VillageListResult


class VillageUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> VillageDto | None:
        ...

    @abstractmethod
    async def find_all(self) -> VillageListResult:
        ...

    @abstractmethod
    async def find_by_code(self, emd_code: str) -> VillageDto | None:
        ...

    @abstractmethod
    async def find_by_region(self, region_id: UUID) -> VillageListResult:
        ...
