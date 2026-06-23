from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.snap_building_repository import SnapBuildingRepository
from apps.townpulse.app.ports.input.snap_building_use_case import SnapBuildingUseCase
from apps.townpulse.app.use_cases.snap_building_interactor import SnapBuildingInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_snap_building_repository(session: AsyncSession = Depends(get_db)) -> SnapBuildingRepository:
    return SnapBuildingRepository(session)


def get_snap_building_use_case(repo: SnapBuildingRepository = Depends(get_snap_building_repository)) -> SnapBuildingUseCase:
    return SnapBuildingInteractor(repo)
