from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.report_orchestrator_schema import ReportBuildRequest, ReportDataResponse
from apps.townpulse.adapter.inbound.mappers.report_orchestrator_mapper import ReportOrchestratorMapper
from apps.townpulse.app.ports.input.report_orchestrator_use_case import ReportOrchestratorUseCase
from apps.townpulse.dependencies.report_orchestrator_provider import get_report_orchestrator_use_case
from core.matrix.grid_trinity_hacker_mixin import WriteUser

report_orchestrator_router = APIRouter(tags=["report_orchestrator"])


@report_orchestrator_router.post("/report-data/{village_code}", response_model=ReportDataResponse)
async def report_data(
    village_code: str,
    body: ReportBuildRequest,
    user: WriteUser,
    use_case: ReportOrchestratorUseCase = Depends(get_report_orchestrator_use_case),
):
    dto = await use_case.build_report_data(village_code, ReportOrchestratorMapper.to_query(body), user)
    if not dto:
        raise HTTPException(status_code=404, detail="마을 또는 TVI 데이터를 찾을 수 없습니다.")
    return ReportOrchestratorMapper.to_response(dto)
