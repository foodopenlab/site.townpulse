from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.snap_building_dto import SnapBuildingDto
from apps.townpulse.app.ports.input.snap_building_use_case import SnapBuildingUseCase
from apps.townpulse.app.ports.output.snap_building_port import SnapBuildingPort


class SnapBuildingInteractor(SnapBuildingUseCase):
    def __init__(self, port: SnapBuildingPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> SnapBuildingDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return SnapBuildingDto(id=entity.id)
