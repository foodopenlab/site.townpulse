from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.organization_repository import OrganizationRepository
from apps.townpulse.app.ports.input.organization_use_case import OrganizationUseCase
from apps.townpulse.app.use_cases.organization_interactor import OrganizationInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_organization_repository(session: AsyncSession = Depends(get_db)) -> OrganizationRepository:
    return OrganizationRepository(session)


def get_organization_use_case(repo: OrganizationRepository = Depends(get_organization_repository)) -> OrganizationUseCase:
    return OrganizationInteractor(repo)
