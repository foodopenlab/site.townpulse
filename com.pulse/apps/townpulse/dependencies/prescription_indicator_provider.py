from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.prescription_indicator_repository import PrescriptionIndicatorRepository
from apps.townpulse.app.ports.input.prescription_indicator_use_case import PrescriptionIndicatorUseCase
from apps.townpulse.app.use_cases.prescription_indicator_interactor import PrescriptionIndicatorInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_prescription_indicator_repository(session: AsyncSession = Depends(get_db)) -> PrescriptionIndicatorRepository:
    return PrescriptionIndicatorRepository(session)


def get_prescription_indicator_use_case(repo: PrescriptionIndicatorRepository = Depends(get_prescription_indicator_repository)) -> PrescriptionIndicatorUseCase:
    return PrescriptionIndicatorInteractor(repo)
