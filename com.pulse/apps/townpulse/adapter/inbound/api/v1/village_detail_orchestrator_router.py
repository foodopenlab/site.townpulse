from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.village_detail_orchestrator_schema import VillageDetailResponse
from apps.townpulse.adapter.inbound.mappers.village_detail_orchestrator_mapper import VillageDetailOrchestratorMapper
from apps.townpulse.app.ports.input.village_detail_orchestrator_use_case import VillageDetailOrchestratorUseCase
from apps.townpulse.dependencies.village_detail_orchestrator_provider import (
    get_village_detail_orchestrator_use_case,
)
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

village_detail_orchestrator_router = APIRouter(tags=["village_detail_orchestrator"])


@village_detail_orchestrator_router.get("/village-detail/{village_code}", response_model=VillageDetailResponse)
async def village_detail(
    village_code: str,
    _user: CurrentUser,
    use_case: VillageDetailOrchestratorUseCase = Depends(get_village_detail_orchestrator_use_case),
):
    dto = await use_case.get_village_detail(village_code)
    if not dto:
        raise HTTPException(status_code=404, detail="마을을 찾을 수 없습니다.")
    return VillageDetailOrchestratorMapper.to_response(dto)
