from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.snap_transport_repository import SnapTransportRepository
from apps.townpulse.app.ports.input.snap_transport_use_case import SnapTransportUseCase
from apps.townpulse.app.use_cases.snap_transport_interactor import SnapTransportInteractor
from core.matrix.grid_oracle_database_manager import get_db


def get_snap_transport_repository(session: AsyncSession = Depends(get_db)) -> SnapTransportRepository:
    return SnapTransportRepository(session)


def get_snap_transport_use_case(repo: SnapTransportRepository = Depends(get_snap_transport_repository)) -> SnapTransportUseCase:
    return SnapTransportInteractor(repo)
