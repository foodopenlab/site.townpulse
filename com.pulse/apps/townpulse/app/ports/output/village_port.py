from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.village_entity import VillageEntity


class VillagePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> VillageEntity | None:
        ...

    @abstractmethod
    async def find_all(self) -> list[VillageEntity]:
        ...

    @abstractmethod
    async def find_by_code(self, emd_code: str) -> VillageEntity | None:
        ...

    @abstractmethod
    async def find_by_region(self, region_id: UUID) -> list[VillageEntity]:
        ...

    @abstractmethod
    async def find_all_for_geocode_sync(self) -> list[VillageEntity]:
        ...

    @abstractmethod
    async def update_geocode_from_vworld(self, village_id: UUID) -> None:
        ...

    @abstractmethod
    async def resolve_legal_dong_codes(self, household_api_key: str) -> int:
        ...

    @abstractmethod
    async def update_emd_code(self, village_id: UUID, emd_code: str) -> None:
        ...
