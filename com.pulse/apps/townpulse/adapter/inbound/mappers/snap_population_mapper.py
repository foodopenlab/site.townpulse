from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.snap_population_schema import SnapPopulationResponse
from apps.townpulse.app.dtos.snap_population_dto import SnapPopulationDto


class SnapPopulationMapper:
    @staticmethod
    def to_response(dto: SnapPopulationDto) -> SnapPopulationResponse:
        return SnapPopulationResponse(id=str(dto.id))
