from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.village_repository import VillageRepository
from apps.townpulse.app.ports.input.village_use_case import VillageUseCase
from apps.townpulse.app.use_cases.village_interactor import VillageInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_village_repository(session: AsyncSession = Depends(get_db)) -> VillageRepository:
    return VillageRepository(session)


def get_village_use_case(repo: VillageRepository = Depends(get_village_repository)) -> VillageUseCase:
    return VillageInteractor(repo)
