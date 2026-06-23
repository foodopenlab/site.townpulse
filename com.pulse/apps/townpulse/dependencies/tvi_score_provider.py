from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.tvi_score_repository import TviScoreRepository
from apps.townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.app.use_cases.tvi_score_interactor import TviScoreInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_tvi_score_repository(session: AsyncSession = Depends(get_db)) -> TviScorePort:
    return TviScoreRepository(session)


def get_tvi_score_use_case(repo: TviScorePort = Depends(get_tvi_score_repository)) -> TviScoreUseCase:
    return TviScoreInteractor(repo)
