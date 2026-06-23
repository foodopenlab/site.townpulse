from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.prescription_fund_source_dto import PrescriptionFundSourceDto
from apps.townpulse.app.ports.input.prescription_fund_source_use_case import PrescriptionFundSourceUseCase
from apps.townpulse.app.ports.output.prescription_fund_source_port import PrescriptionFundSourcePort


class PrescriptionFundSourceInteractor(PrescriptionFundSourceUseCase):
    def __init__(self, port: PrescriptionFundSourcePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> PrescriptionFundSourceDto | None:
        entity = await self._port.find_by_id(entity_id)
        if entity is None:
            return None
        return PrescriptionFundSourceDto(id=entity.id)
