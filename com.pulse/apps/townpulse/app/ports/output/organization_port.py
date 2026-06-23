from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.organization_entity import OrganizationEntity


class OrganizationPort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> OrganizationEntity | None:
        ...
