from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.subscription_repository import SubscriptionRepository
from apps.townpulse.app.ports.input.subscription_use_case import SubscriptionUseCase
from apps.townpulse.app.use_cases.subscription_interactor import SubscriptionInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_subscription_repository(session: AsyncSession = Depends(get_db)) -> SubscriptionRepository:
    return SubscriptionRepository(session)


def get_subscription_use_case(repo: SubscriptionRepository = Depends(get_subscription_repository)) -> SubscriptionUseCase:
    return SubscriptionInteractor(repo)
