from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.report_schema import ReportResponse
from apps.townpulse.app.dtos.report_dto import ReportDto


class ReportMapper:
    @staticmethod
    def to_response(dto: ReportDto) -> ReportResponse:
        return ReportResponse(id=str(dto.id))
