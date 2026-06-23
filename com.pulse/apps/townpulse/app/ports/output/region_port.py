from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.region_entity import RegionEntity


class RegionPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> RegionEntity | None:
        ...

    @abstractmethod
    async def find_all(self) -> list[RegionEntity]:
        ...

    @abstractmethod
    async def find_by_emd_code(self, emd_code: str) -> RegionEntity | None:
        ...

    @abstractmethod
    async def find_all_legal_dong_codes(self) -> list[str]:
        ...

    @abstractmethod
    async def ingest_fiscal_self_reliance(self) -> None:
        ...
