from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.budget_unit_price_repository import BudgetUnitPriceRepository
from apps.townpulse.app.ports.input.budget_unit_price_use_case import BudgetUnitPriceUseCase
from apps.townpulse.app.use_cases.budget_unit_price_interactor import BudgetUnitPriceInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_budget_unit_price_repository(session: AsyncSession = Depends(get_db)) -> BudgetUnitPriceRepository:
    return BudgetUnitPriceRepository(session)


def get_budget_unit_price_use_case(repo: BudgetUnitPriceRepository = Depends(get_budget_unit_price_repository)) -> BudgetUnitPriceUseCase:
    return BudgetUnitPriceInteractor(repo)
