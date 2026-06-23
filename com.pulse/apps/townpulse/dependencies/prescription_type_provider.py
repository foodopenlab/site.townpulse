from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.prescription_type_repository import PrescriptionTypeRepository
from apps.townpulse.app.ports.input.prescription_type_use_case import PrescriptionTypeUseCase
from apps.townpulse.app.use_cases.prescription_type_interactor import PrescriptionTypeInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_prescription_type_repository(session: AsyncSession = Depends(get_db)) -> PrescriptionTypeRepository:
    return PrescriptionTypeRepository(session)


def get_prescription_type_use_case(repo: PrescriptionTypeRepository = Depends(get_prescription_type_repository)) -> PrescriptionTypeUseCase:
    return PrescriptionTypeInteractor(repo)
