from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.snap_building_schema import SnapBuildingResponse
from apps.townpulse.app.dtos.snap_building_dto import SnapBuildingDto


class SnapBuildingMapper:
    @staticmethod
    def to_response(dto: SnapBuildingDto) -> SnapBuildingResponse:
        return SnapBuildingResponse(id=str(dto.id))
