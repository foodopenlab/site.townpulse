from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.prescription_fund_source_schema import PrescriptionFundSourceResponse
from apps.townpulse.app.dtos.prescription_fund_source_dto import PrescriptionFundSourceDto


class PrescriptionFundSourceMapper:
    @staticmethod
    def to_response(dto: PrescriptionFundSourceDto) -> PrescriptionFundSourceResponse:
        return PrescriptionFundSourceResponse(id=str(dto.id))
