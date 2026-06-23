from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.prescription_indicator_dto import PrescriptionIndicatorDto
from apps.townpulse.app.ports.input.prescription_indicator_use_case import PrescriptionIndicatorUseCase
from apps.townpulse.app.ports.output.prescription_indicator_port import PrescriptionIndicatorPort


class PrescriptionIndicatorInteractor(PrescriptionIndicatorUseCase):
    def __init__(self, port: PrescriptionIndicatorPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> PrescriptionIndicatorDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return PrescriptionIndicatorDto(id=entity.id)
