from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.prescription_fund_source_port import PrescriptionFundSourcePort
from apps.townpulse.domain.entities.prescription_fund_source_entity import PrescriptionFundSourceEntity


class PrescriptionFundSourceRepository(PrescriptionFundSourcePort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> PrescriptionFundSourceEntity | None:
        return None
