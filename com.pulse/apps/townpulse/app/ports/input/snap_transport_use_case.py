from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.snap_transport_dto import SnapTransportDto


class SnapTransportUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> SnapTransportDto | None:
        ...
