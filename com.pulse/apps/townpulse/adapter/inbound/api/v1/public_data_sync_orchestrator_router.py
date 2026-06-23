from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from apps.townpulse.adapter.inbound.api.schemas.public_data_sync_orchestrator_schema import (
    SyncJobLatestResponse,
    SyncJobResponse,
)
from apps.townpulse.adapter.inbound.mappers.public_data_sync_orchestrator_mapper import PublicDataSyncOrchestratorMapper
from apps.townpulse.app.ports.input.public_data_sync_orchestrator_use_case import PublicDataSyncOrchestratorUseCase
from apps.townpulse.dependencies.public_data_sync_orchestrator_provider import (
    get_public_data_sync_orchestrator_use_case,
    run_collect_all_background,
    run_collect_all_core_background,
)
from core.matrix.grid_trinity_hacker_mixin import CurrentUser, WriteUser

public_data_sync_orchestrator_router = APIRouter(prefix="/admin/sync", tags=["public_data_sync_orchestrator"])


@public_data_sync_orchestrator_router.post("/trigger", response_model=SyncJobResponse, status_code=202)
async def admin_sync_trigger(
    background_tasks: BackgroundTasks,
    _user: WriteUser,
):
    """전체 Phase A — 백그라운드 실행. 진행은 GET /jobs/latest 로 확인."""
    background_tasks.add_task(run_collect_all_background)
    return SyncJobResponse(status="ACCEPTED")


@public_data_sync_orchestrator_router.post("/trigger-core", response_model=SyncJobResponse, status_code=202)
async def admin_sync_trigger_core(
    background_tasks: BackgroundTasks,
    _user: CurrentUser,
    offset: int | None = Query(None, ge=0, description="동기화 시작할 마을 오프셋"),
    limit: int | None = Query(None, ge=1, le=228, description="동기화할 마을 수 (개발용, Phase A)"),
    sync_dong_code: bool = Query(True, description="법정동코드 매핑 실행 여부"),
    sync_core: bool = Query(True, description="인구/건축/통계 SNAP 동기화 여부"),
    sync_transport: bool = Query(True, description="교통 SNAP 동기화 여부"),
    sigungu_code: str | None = Query(None, min_length=5, max_length=5, description="동기화할 특정 시군구 코드 (5자리)"),
    sync_tvi: bool = Query(True, description="TVI 점수 재계산 여부"),
):
    """Phase A — vworld·인구·건축·통계·교통 SNAP. demo/QA 토큰 가능. 백그라운드 실행."""
    background_tasks.add_task(
        run_collect_all_core_background,
        offset=offset,
        limit=limit,
        sync_dong_code=sync_dong_code,
        sync_core=sync_core,
        sync_transport=sync_transport,
        sigungu_code=sigungu_code,
        sync_tvi=sync_tvi,
    )
    return SyncJobResponse(status="ACCEPTED")


@public_data_sync_orchestrator_router.post("/migration-chunk/{chunk_index}", response_model=SyncJobResponse)
async def admin_sync_migration_chunk(
    chunk_index: int,
    _user: WriteUser,
    use_case: PublicDataSyncOrchestratorUseCase = Depends(get_public_data_sync_orchestrator_use_case),
):
    """Phase B — API#4 net_youth_migration (chunk 0~9)."""
    if chunk_index not in range(10):
        raise HTTPException(status_code=400, detail="chunk_index는 0부터 9 사이여야 합니다.")
    result = await use_case.collect_migration_chunk(chunk_index)
    return PublicDataSyncOrchestratorMapper.to_trigger_response(result)


@public_data_sync_orchestrator_router.post("/finalize", response_model=SyncJobResponse)
async def admin_sync_finalize(
    _user: WriteUser,
    use_case: PublicDataSyncOrchestratorUseCase = Depends(get_public_data_sync_orchestrator_use_case),
):
    """Phase C — migration 완료 후 TVI 재계산."""
    result = await use_case.finalize_monthly_snap()
    return PublicDataSyncOrchestratorMapper.to_trigger_response(result)


@public_data_sync_orchestrator_router.post("/trigger-fiscal", response_model=SyncJobResponse)
async def admin_sync_trigger_fiscal(
    _user: WriteUser,
    use_case: PublicDataSyncOrchestratorUseCase = Depends(get_public_data_sync_orchestrator_use_case),
):
    """연 1회 — REGION 재정자립도(API#5)."""
    result = await use_case.ingest_fiscal_all()
    return PublicDataSyncOrchestratorMapper.to_trigger_response(result)


@public_data_sync_orchestrator_router.get("/jobs/latest", response_model=SyncJobLatestResponse)
async def admin_sync_latest(
    _user: CurrentUser,
    use_case: PublicDataSyncOrchestratorUseCase = Depends(get_public_data_sync_orchestrator_use_case),
):
    job = await use_case.get_latest_job()
    if not job:
        raise HTTPException(status_code=404, detail="동기화 이력이 없습니다.")
    return PublicDataSyncOrchestratorMapper.to_latest_job_response(job)


@public_data_sync_orchestrator_router.get("/jobs/{job_id}", response_model=SyncJobLatestResponse)
async def admin_sync_job_by_id(
    job_id: UUID,
    _user: CurrentUser,
    use_case: PublicDataSyncOrchestratorUseCase = Depends(get_public_data_sync_orchestrator_use_case),
):
    job = await use_case.get_job_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="동기화 job을 찾을 수 없습니다.")
    return PublicDataSyncOrchestratorMapper.to_latest_job_response(job)
