from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.region_repository import RegionRepository
from apps.townpulse.app.ports.input.region_use_case import RegionUseCase
from apps.townpulse.app.use_cases.region_interactor import RegionInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_region_repository(session: AsyncSession = Depends(get_db)) -> RegionRepository:
    return RegionRepository(session)


def get_region_use_case(repo: RegionRepository = Depends(get_region_repository)) -> RegionUseCase:
    return RegionInteractor(repo)
