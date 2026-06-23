from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.village_schema import VillageDetailResponse, VillageListItemResponse
from apps.townpulse.adapter.inbound.mappers.village_mapper import VillageMapper
from apps.townpulse.app.ports.input.village_use_case import VillageUseCase
from apps.townpulse.dependencies.village_provider import get_village_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

village_router = APIRouter(prefix="/villages", tags=["village"])


@village_router.get("", response_model=list[VillageListItemResponse])
async def list_villages(
    _user: CurrentUser,
    use_case: VillageUseCase = Depends(get_village_use_case),
):
    result = await use_case.find_all()
    return [VillageMapper.to_list_item(item) for item in result.items]


@village_router.get("/by-region/{region_id}", response_model=list[VillageListItemResponse])
async def list_villages_by_region(
    region_id: UUID,
    _user: CurrentUser,
    use_case: VillageUseCase = Depends(get_village_use_case),
):
    result = await use_case.find_by_region(region_id)
    return [VillageMapper.to_list_item(item) for item in result.items]


@village_router.get("/{emd_code}", response_model=VillageDetailResponse)
async def get_village_by_code(
    emd_code: str,
    _user: CurrentUser,
    use_case: VillageUseCase = Depends(get_village_use_case),
):
    dto = await use_case.find_by_code(emd_code)
    if not dto:
        raise HTTPException(status_code=404, detail="마을을 찾을 수 없습니다.")
    return VillageMapper.to_detail_response(dto)
