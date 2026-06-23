from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.snap_statistics_schema import SnapStatisticsResponse
from apps.townpulse.app.dtos.snap_statistics_dto import SnapStatisticsDto


class SnapStatisticsMapper:
    @staticmethod
    def to_response(dto: SnapStatisticsDto) -> SnapStatisticsResponse:
        return SnapStatisticsResponse(id=str(dto.id))
