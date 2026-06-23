from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.dashboard_orchestrator_repository import (
    DashboardOrchestratorRepository,
)
from apps.townpulse.app.ports.input.dashboard_orchestrator_use_case import DashboardOrchestratorUseCase
from apps.townpulse.app.use_cases.dashboard_orchestrator_interactor import DashboardOrchestratorInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_dashboard_orchestrator_repository(
    session: AsyncSession = Depends(get_db),
) -> DashboardOrchestratorRepository:
    return DashboardOrchestratorRepository(session)


def get_dashboard_orchestrator_use_case(
    repo: DashboardOrchestratorRepository = Depends(get_dashboard_orchestrator_repository),
) -> DashboardOrchestratorUseCase:
    return DashboardOrchestratorInteractor(repo)
