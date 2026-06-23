from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.prescription_fund_source_repository import PrescriptionFundSourceRepository
from apps.townpulse.app.ports.input.prescription_fund_source_use_case import PrescriptionFundSourceUseCase
from apps.townpulse.app.use_cases.prescription_fund_source_interactor import PrescriptionFundSourceInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_prescription_fund_source_repository(session: AsyncSession = Depends(get_db)) -> PrescriptionFundSourceRepository:
    return PrescriptionFundSourceRepository(session)


def get_prescription_fund_source_use_case(repo: PrescriptionFundSourceRepository = Depends(get_prescription_fund_source_repository)) -> PrescriptionFundSourceUseCase:
    return PrescriptionFundSourceInteractor(repo)
