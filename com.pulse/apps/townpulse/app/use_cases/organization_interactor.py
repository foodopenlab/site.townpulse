from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.organization_dto import OrganizationDto
from apps.townpulse.app.ports.input.organization_use_case import OrganizationUseCase
from apps.townpulse.app.ports.output.organization_port import OrganizationPort


class OrganizationInteractor(OrganizationUseCase):
    def __init__(self, port: OrganizationPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> OrganizationDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return OrganizationDto(id=entity.id)
