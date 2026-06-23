from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.snap_statistics_dto import SnapStatisticsDto
from apps.townpulse.app.ports.input.snap_statistics_use_case import SnapStatisticsUseCase
from apps.townpulse.app.ports.output.snap_statistics_port import SnapStatisticsPort


class SnapStatisticsInteractor(SnapStatisticsUseCase):
    def __init__(self, port: SnapStatisticsPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> SnapStatisticsDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return SnapStatisticsDto(id=entity.id)
