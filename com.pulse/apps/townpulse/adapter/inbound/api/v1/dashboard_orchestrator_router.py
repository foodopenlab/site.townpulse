from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.dashboard_orchestrator_schema import (
    DashboardSummaryResponse,
    VillageListItemResponse,
    VillageMapSummaryResponse,
)
from apps.townpulse.adapter.inbound.mappers.dashboard_orchestrator_mapper import DashboardOrchestratorMapper
from apps.townpulse.app.ports.input.dashboard_orchestrator_use_case import DashboardOrchestratorUseCase
from apps.townpulse.dependencies.dashboard_orchestrator_provider import get_dashboard_orchestrator_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

dashboard_orchestrator_router = APIRouter(prefix="/dashboard", tags=["dashboard_orchestrator"])


@dashboard_orchestrator_router.get("/summary", response_model=DashboardSummaryResponse)
async def dashboard_summary(
    _user: CurrentUser,
    use_case: DashboardOrchestratorUseCase = Depends(get_dashboard_orchestrator_use_case),
):
    return DashboardOrchestratorMapper.to_summary_response(await use_case.get_summary())


@dashboard_orchestrator_router.get("/map/villages", response_model=list[VillageListItemResponse])
async def map_villages(
    _user: CurrentUser,
    use_case: DashboardOrchestratorUseCase = Depends(get_dashboard_orchestrator_use_case),
    grade: str | None = None,
    sigun: str | None = None,
):
    items = await use_case.get_map_villages(grade, sigun)
    return [DashboardOrchestratorMapper.to_village_list_item(i) for i in items]


@dashboard_orchestrator_router.get("/map/villages/{village_code}", response_model=VillageMapSummaryResponse)
async def map_village_summary(
    village_code: str,
    _user: CurrentUser,
    use_case: DashboardOrchestratorUseCase = Depends(get_dashboard_orchestrator_use_case),
):
    dto = await use_case.get_village_summary_card(village_code)
    if not dto:
        raise HTTPException(status_code=404, detail="마을을 찾을 수 없습니다.")
    return DashboardOrchestratorMapper.to_map_summary(dto)
