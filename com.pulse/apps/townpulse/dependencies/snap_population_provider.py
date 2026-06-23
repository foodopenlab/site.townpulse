from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.snap_population_repository import SnapPopulationRepository
from apps.townpulse.app.ports.input.snap_population_use_case import SnapPopulationUseCase
from apps.townpulse.app.use_cases.snap_population_interactor import SnapPopulationInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_snap_population_repository(session: AsyncSession = Depends(get_db)) -> SnapPopulationRepository:
    return SnapPopulationRepository(session)


def get_snap_population_use_case(repo: SnapPopulationRepository = Depends(get_snap_population_repository)) -> SnapPopulationUseCase:
    return SnapPopulationInteractor(repo)
