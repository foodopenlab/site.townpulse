from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapStatisticsOrm
from apps.townpulse.adapter.outbound.repositories.snap_read_helpers import find_latest
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

snap_statistics_router = APIRouter(prefix="/snap/statistics", tags=["snap_statistics"])

_STATS_FIELDS = ("snapshot_date", "aging_ratio", "youth_ratio", "pop_density")


@snap_statistics_router.get("/{village_id}/latest")
async def get_latest_statistics(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    row = await find_latest(session, SnapStatisticsOrm, UUID(village_id), _STATS_FIELDS)
    if not row:
        raise HTTPException(status_code=404, detail="통계 스냅샷이 없습니다.")
    return row
