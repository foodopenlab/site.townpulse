from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapBuildingOrm
from apps.townpulse.adapter.outbound.repositories.snap_read_helpers import find_latest
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

snap_building_router = APIRouter(prefix="/snap/building", tags=["snap_building"])

_BUILDING_FIELDS = ("snapshot_date", "residential_buildings")


@snap_building_router.get("/{village_id}/latest")
async def get_latest_building(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    row = await find_latest(session, SnapBuildingOrm, UUID(village_id), _BUILDING_FIELDS)
    if not row:
        raise HTTPException(status_code=404, detail="건물 스냅샷이 없습니다.")
    return row
