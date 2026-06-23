from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.region_schema import RegionDetailResponse, RegionListItemResponse
from apps.townpulse.adapter.inbound.mappers.region_mapper import RegionMapper
from apps.townpulse.app.ports.input.region_use_case import RegionUseCase
from apps.townpulse.dependencies.region_provider import get_region_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

region_router = APIRouter(prefix="/regions", tags=["region"])


@region_router.get("", response_model=list[RegionListItemResponse])
async def list_regions(
    _user: CurrentUser,
    use_case: RegionUseCase = Depends(get_region_use_case),
):
    result = await use_case.find_all()
    return [RegionMapper.to_list_item(item) for item in result.items]


@region_router.get("/{emd_code}", response_model=RegionDetailResponse)
async def get_region_by_emd_code(
    emd_code: str,
    _user: CurrentUser,
    use_case: RegionUseCase = Depends(get_region_use_case),
):
    dto = await use_case.find_by_emd_code(emd_code)
    if not dto:
        raise HTTPException(status_code=404, detail="행정구역을 찾을 수 없습니다.")
    return RegionMapper.to_detail_response(dto)
