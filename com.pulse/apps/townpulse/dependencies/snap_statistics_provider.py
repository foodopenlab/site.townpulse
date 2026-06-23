from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.snap_statistics_repository import SnapStatisticsRepository
from apps.townpulse.app.ports.input.snap_statistics_use_case import SnapStatisticsUseCase
from apps.townpulse.app.use_cases.snap_statistics_interactor import SnapStatisticsInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_snap_statistics_repository(session: AsyncSession = Depends(get_db)) -> SnapStatisticsRepository:
    return SnapStatisticsRepository(session)


def get_snap_statistics_use_case(repo: SnapStatisticsRepository = Depends(get_snap_statistics_repository)) -> SnapStatisticsUseCase:
    return SnapStatisticsInteractor(repo)
