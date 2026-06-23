from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.user_repository import UserRepository
from apps.townpulse.app.ports.input.user_use_case import UserUseCase
from apps.townpulse.app.use_cases.user_interactor import UserInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(session)


def get_user_use_case(repo: UserRepository = Depends(get_user_repository)) -> UserUseCase:
    return UserInteractor(repo)
