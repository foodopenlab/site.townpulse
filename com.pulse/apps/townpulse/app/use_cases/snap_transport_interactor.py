from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.snap_transport_dto import SnapTransportDto
from apps.townpulse.app.ports.input.snap_transport_use_case import SnapTransportUseCase
from apps.townpulse.app.ports.output.snap_transport_port import SnapTransportPort


class SnapTransportInteractor(SnapTransportUseCase):
    def __init__(self, port: SnapTransportPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> SnapTransportDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return SnapTransportDto(id=entity.id)
