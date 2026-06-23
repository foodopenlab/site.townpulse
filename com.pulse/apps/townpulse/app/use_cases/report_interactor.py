from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.report_dto import ReportDto
from apps.townpulse.app.ports.input.report_use_case import ReportUseCase
from apps.townpulse.app.ports.output.report_port import ReportPort


class ReportInteractor(ReportUseCase):
    def __init__(self, port: ReportPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> ReportDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return ReportDto(id=entity.id)
