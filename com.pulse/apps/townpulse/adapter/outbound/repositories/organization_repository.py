from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.organization_port import OrganizationPort
from apps.townpulse.domain.entities.organization_entity import OrganizationEntity


class OrganizationRepository(OrganizationPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> OrganizationEntity | None:
        return None
