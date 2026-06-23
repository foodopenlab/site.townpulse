from __future__ import annotations

import asyncio
import logging
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from apps.townpulse.adapter.outbound.repositories.public_data_sync_orchestrator_repository import (
    PublicDataSyncOrchestratorRepository,
)
from apps.townpulse.adapter.outbound.repositories.region_repository import RegionRepository
from apps.townpulse.adapter.outbound.repositories.snap_building_repository import SnapBuildingRepository
from apps.townpulse.adapter.outbound.repositories.snap_population_repository import SnapPopulationRepository
from apps.townpulse.adapter.outbound.repositories.snap_statistics_repository import SnapStatisticsRepository
from apps.townpulse.adapter.outbound.repositories.snap_transport_repository import SnapTransportRepository
from apps.townpulse.adapter.outbound.repositories.tvi_score_repository import TviScoreRepository
from apps.townpulse.adapter.outbound.repositories.village_repository import VillageRepository
from apps.townpulse.app.ports.input.public_data_sync_orchestrator_use_case import PublicDataSyncOrchestratorUseCase
from apps.townpulse.app.ports.output.public_data_sync_orchestrator_port import PublicDataSyncOrchestratorPort
from apps.townpulse.app.ports.output.region_port import RegionPort
from apps.townpulse.app.ports.output.snap_building_port import SnapBuildingPort
from apps.townpulse.app.ports.output.snap_population_port import SnapPopulationPort
from apps.townpulse.app.ports.output.snap_statistics_port import SnapStatisticsPort
from apps.townpulse.app.ports.output.snap_transport_port import SnapTransportPort
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.app.ports.output.village_port import VillagePort
from apps.townpulse.app.use_cases.public_data_sync_orchestrator_interactor import PublicDataSyncOrchestratorInteractor
from apps.townpulse.dependencies.region_provider import get_region_repository
from apps.townpulse.dependencies.snap_building_provider import get_snap_building_repository
from apps.townpulse.dependencies.snap_population_provider import get_snap_population_repository
from apps.townpulse.dependencies.snap_statistics_provider import get_snap_statistics_repository
from apps.townpulse.dependencies.snap_transport_provider import get_snap_transport_repository
from apps.townpulse.dependencies.tvi_score_provider import get_tvi_score_repository
from apps.townpulse.dependencies.village_provider import get_village_repository
from core.matrix.grid_oracle_database_manager import get_db, get_session_factory

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
_sync_lock = asyncio.Lock()
_sync_running = False


async def run_collect_all_core_background(
    *,
    offset: int | None = None,
    limit: int | None = None,
    sync_dong_code: bool = True,
    sync_core: bool = True,
    sync_transport: bool = True,
    sigungu_code: str | None = None,
    sync_tvi: bool = True,
) -> None:
    """HTTP와 분리된 세션에서 Phase A 실행 — 대시보드 등 API 응답 블로킹 방지."""
    global _sync_running
    async with _sync_lock:
        if _sync_running:
            logger.warning("collect_all_core already running; duplicate request skipped")
            return
        _sync_running = True
    try:
        factory = get_session_factory()
        async with factory() as session:
            interactor = build_public_data_sync_interactor(session)
            try:
                await interactor.collect_all_core(
                    offset=offset,
                    limit=limit,
                    sync_dong_code=sync_dong_code,
                    sync_core=sync_core,
                    sync_transport=sync_transport,
                    sigungu_code=sigungu_code,
                    sync_tvi=sync_tvi,
                )
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    finally:
        _sync_running = False


async def run_collect_all_background() -> None:
    await run_collect_all_core_background(
        offset=None,
        limit=None,
        sync_dong_code=True,
        sync_core=True,
        sync_transport=True,
        sigungu_code=None,
        sync_tvi=True,
    )


def get_public_data_sync_orchestrator_repository(
    session: AsyncSession = Depends(get_db),
) -> PublicDataSyncOrchestratorPort:
    return PublicDataSyncOrchestratorRepository(session)


def get_public_data_sync_orchestrator_use_case(
    sync_port: PublicDataSyncOrchestratorPort = Depends(get_public_data_sync_orchestrator_repository),
    region_port: RegionPort = Depends(get_region_repository),
    village_port: VillagePort = Depends(get_village_repository),
    snap_population_port: SnapPopulationPort = Depends(get_snap_population_repository),
    snap_building_port: SnapBuildingPort = Depends(get_snap_building_repository),
    snap_transport_port: SnapTransportPort = Depends(get_snap_transport_repository),
    snap_statistics_port: SnapStatisticsPort = Depends(get_snap_statistics_repository),
    tvi_score_port: TviScorePort = Depends(get_tvi_score_repository),
) -> PublicDataSyncOrchestratorUseCase:
    return PublicDataSyncOrchestratorInteractor(
        sync_port,
        region_port,
        village_port,
        snap_population_port,
        snap_building_port,
        snap_transport_port,
        snap_statistics_port,
        tvi_score_port,
    )


def build_public_data_sync_interactor(session: AsyncSession) -> PublicDataSyncOrchestratorInteractor:
    return PublicDataSyncOrchestratorInteractor(
        PublicDataSyncOrchestratorRepository(session),
        RegionRepository(session),
        VillageRepository(session),
        SnapPopulationRepository(session),
        SnapBuildingRepository(session),
        SnapTransportRepository(session),
        SnapStatisticsRepository(session),
        TviScoreRepository(session),
    )


async def run_scheduled_collect_all() -> None:
    factory = get_session_factory()
    async with factory() as session:
        interactor = build_public_data_sync_interactor(session)
        await interactor.collect_all()
        await session.commit()


async def run_scheduled_ingest_fiscal_all() -> None:
    factory = get_session_factory()
    async with factory() as session:
        interactor = build_public_data_sync_interactor(session)
        await interactor.ingest_fiscal_all()
        await session.commit()


def register_batch_jobs() -> None:
    if scheduler.get_job("snap_monthly"):
        return
    scheduler.add_job(run_scheduled_collect_all, "cron", day=1, hour=3, id="snap_monthly")
    scheduler.add_job(run_scheduled_ingest_fiscal_all, "cron", month=1, day=1, hour=4, id="region_fiscal_yearly")
