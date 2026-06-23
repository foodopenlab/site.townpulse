from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapTransportOrm
from apps.townpulse.adapter.outbound.repositories.snap_read_helpers import find_latest
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

snap_transport_router = APIRouter(prefix="/snap/transport", tags=["snap_transport"])

_TRANSPORT_FIELDS = (
    "snapshot_date",
    "bus_route_count",
    "avg_bus_interval_min",
    "nearest_stop_distance_m",
    "bus_stops_within_1km",
)


@snap_transport_router.get("/{village_id}/latest")
async def get_latest_transport(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    row = await find_latest(session, SnapTransportOrm, UUID(village_id), _TRANSPORT_FIELDS)
    if not row:
        raise HTTPException(status_code=404, detail="교통 스냅샷이 없습니다.")
    return row
