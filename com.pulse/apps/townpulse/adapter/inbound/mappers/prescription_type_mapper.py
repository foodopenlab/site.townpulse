from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.prescription_type_schema import (
    PrescriptionTypeDetailResponse,
    PrescriptionTypeListItemResponse,
)
from apps.townpulse.app.dtos.prescription_type_dto import PrescriptionTypeDto


class PrescriptionTypeMapper:
    @staticmethod
    def to_list_item(dto: PrescriptionTypeDto) -> PrescriptionTypeListItemResponse:
        return PrescriptionTypeListItemResponse(code=dto.code, name=dto.name, category=dto.category)

    @staticmethod
    def to_detail_response(dto: PrescriptionTypeDto) -> PrescriptionTypeDetailResponse:
        return PrescriptionTypeDetailResponse(
            id=str(dto.id),
            code=dto.code,
            name=dto.name,
            category=dto.category,
            rollout_timeline=dto.rollout_timeline,
            is_active=dto.is_active,
        )
