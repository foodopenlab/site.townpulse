from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.app.ports.output.report_port import ReportPort
from apps.townpulse.domain.entities.report_entity import ReportEntity


class ReportRepository(ReportPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> ReportEntity | None:
        return None
