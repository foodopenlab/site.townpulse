from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapPopulationOrm
from apps.townpulse.adapter.outbound.repositories.snap_read_helpers import find_history, find_latest
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

snap_population_router = APIRouter(prefix="/snap/population", tags=["snap_population"])

_POP_FIELDS = (
    "snapshot_date",
    "population_total",
    "population_65plus",
    "population_youth",
    "registered_households",
    "net_youth_migration",
)


@snap_population_router.get("/{village_id}/latest")
async def get_latest_population(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    row = await find_latest(session, SnapPopulationOrm, UUID(village_id), _POP_FIELDS)
    if not row:
        raise HTTPException(status_code=404, detail="인구 스냅샷이 없습니다.")
    return row


@snap_population_router.get("/{village_id}/history")
async def get_population_history(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    return await find_history(session, SnapPopulationOrm, UUID(village_id), _POP_FIELDS)
