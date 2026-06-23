from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.report_orchestrator_repository import ReportOrchestratorRepository
from apps.townpulse.app.ports.input.report_orchestrator_use_case import ReportOrchestratorUseCase
from apps.townpulse.app.use_cases.report_orchestrator_interactor import ReportOrchestratorInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_report_orchestrator_repository(session: AsyncSession = Depends(get_db)) -> ReportOrchestratorRepository:
    return ReportOrchestratorRepository(session)


def get_report_orchestrator_use_case(
    repo: ReportOrchestratorRepository = Depends(get_report_orchestrator_repository),
) -> ReportOrchestratorUseCase:
    return ReportOrchestratorInteractor(repo)
