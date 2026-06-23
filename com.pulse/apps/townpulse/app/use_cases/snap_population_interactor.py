from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.snap_population_dto import SnapPopulationDto
from apps.townpulse.app.ports.input.snap_population_use_case import SnapPopulationUseCase
from apps.townpulse.app.ports.output.snap_population_port import SnapPopulationPort


class SnapPopulationInteractor(SnapPopulationUseCase):
    def __init__(self, port: SnapPopulationPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> SnapPopulationDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return SnapPopulationDto(id=entity.id)
