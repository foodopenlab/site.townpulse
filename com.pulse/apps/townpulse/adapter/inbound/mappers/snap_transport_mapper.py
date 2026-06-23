from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.snap_transport_schema import SnapTransportResponse
from apps.townpulse.app.dtos.snap_transport_dto import SnapTransportDto


class SnapTransportMapper:
    @staticmethod
    def to_response(dto: SnapTransportDto) -> SnapTransportResponse:
        return SnapTransportResponse(id=str(dto.id))
