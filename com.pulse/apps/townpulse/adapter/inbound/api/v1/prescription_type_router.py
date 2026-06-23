from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.prescription_type_schema import (
    PrescriptionTypeDetailResponse,
    PrescriptionTypeListItemResponse,
)
from apps.townpulse.adapter.inbound.mappers.prescription_type_mapper import PrescriptionTypeMapper
from apps.townpulse.app.ports.input.prescription_type_use_case import PrescriptionTypeUseCase
from apps.townpulse.dependencies.prescription_type_provider import get_prescription_type_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

prescription_type_router = APIRouter(prefix="/prescription-types", tags=["prescription_type"])


@prescription_type_router.get("", response_model=list[PrescriptionTypeListItemResponse])
async def list_prescription_types(
    _user: CurrentUser,
    use_case: PrescriptionTypeUseCase = Depends(get_prescription_type_use_case),
):
    result = await use_case.find_all_active()
    return [PrescriptionTypeMapper.to_list_item(item) for item in result.items]


@prescription_type_router.get("/{code}", response_model=PrescriptionTypeDetailResponse)
async def get_prescription_type_by_code(
    code: str,
    _user: CurrentUser,
    use_case: PrescriptionTypeUseCase = Depends(get_prescription_type_use_case),
):
    dto = await use_case.find_by_code(code)
    if not dto:
        raise HTTPException(status_code=404, detail="처방 유형을 찾을 수 없습니다.")
    return PrescriptionTypeMapper.to_detail_response(dto)
