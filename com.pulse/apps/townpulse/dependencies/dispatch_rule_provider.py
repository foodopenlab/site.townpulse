from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.dispatch_rule_repository import DispatchRuleRepository
from apps.townpulse.app.ports.input.dispatch_rule_use_case import DispatchRuleUseCase
from apps.townpulse.app.use_cases.dispatch_rule_interactor import DispatchRuleInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_dispatch_rule_repository(session: AsyncSession = Depends(get_db)) -> DispatchRuleRepository:
    return DispatchRuleRepository(session)


def get_dispatch_rule_use_case(repo: DispatchRuleRepository = Depends(get_dispatch_rule_repository)) -> DispatchRuleUseCase:
    return DispatchRuleInteractor(repo)
