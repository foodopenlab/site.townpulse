from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.snap_transport_entity import SnapTransportEntity


class SnapTransportPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapTransportEntity | None:
        ...

    @abstractmethod
    async def ingest_for_village(self, village_id: UUID, *, apply_mock: bool = False) -> None:
        ...
