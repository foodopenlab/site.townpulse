from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.budget_estimate_repository import BudgetEstimateRepository
from apps.townpulse.app.ports.input.budget_estimate_use_case import BudgetEstimateUseCase
from apps.townpulse.app.use_cases.budget_estimate_interactor import BudgetEstimateInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_budget_estimate_repository(session: AsyncSession = Depends(get_db)) -> BudgetEstimateRepository:
    return BudgetEstimateRepository(session)


def get_budget_estimate_use_case(repo: BudgetEstimateRepository = Depends(get_budget_estimate_repository)) -> BudgetEstimateUseCase:
    return BudgetEstimateInteractor(repo)
