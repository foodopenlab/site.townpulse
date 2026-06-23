from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.prescription_indicator_port import PrescriptionIndicatorPort
from apps.townpulse.domain.entities.prescription_indicator_entity import PrescriptionIndicatorEntity


class PrescriptionIndicatorRepository(PrescriptionIndicatorPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> PrescriptionIndicatorEntity | None:
        return None
