from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.village_detail_orchestrator_repository import (
    VillageDetailOrchestratorRepository,
)
from apps.townpulse.app.ports.input.village_detail_orchestrator_use_case import VillageDetailOrchestratorUseCase
from apps.townpulse.app.use_cases.village_detail_orchestrator_interactor import VillageDetailOrchestratorInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_village_detail_orchestrator_repository(
    session: AsyncSession = Depends(get_db),
) -> VillageDetailOrchestratorRepository:
    return VillageDetailOrchestratorRepository(session)


def get_village_detail_orchestrator_use_case(
    repo: VillageDetailOrchestratorRepository = Depends(get_village_detail_orchestrator_repository),
) -> VillageDetailOrchestratorUseCase:
    return VillageDetailOrchestratorInteractor(repo)
