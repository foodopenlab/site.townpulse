from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.organization_dto import OrganizationDto


class OrganizationUseCase(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> OrganizationDto | None:
        ...
