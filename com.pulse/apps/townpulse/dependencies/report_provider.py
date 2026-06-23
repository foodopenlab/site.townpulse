from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.report_repository import ReportRepository
from apps.townpulse.app.ports.input.report_use_case import ReportUseCase
from apps.townpulse.app.use_cases.report_interactor import ReportInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_report_repository(session: AsyncSession = Depends(get_db)) -> ReportRepository:
    return ReportRepository(session)


def get_report_use_case(repo: ReportRepository = Depends(get_report_repository)) -> ReportUseCase:
    return ReportInteractor(repo)
