from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.prescription_indicator_schema import PrescriptionIndicatorResponse
from apps.townpulse.app.dtos.prescription_indicator_dto import PrescriptionIndicatorDto


class PrescriptionIndicatorMapper:
    @staticmethod
    def to_response(dto: PrescriptionIndicatorDto) -> PrescriptionIndicatorResponse:
        return PrescriptionIndicatorResponse(id=str(dto.id))
