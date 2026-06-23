from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import PrescriptionIndicatorOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

prescription_indicator_router = APIRouter(prefix="/prescription-indicators", tags=["prescription_indicator"])


@prescription_indicator_router.get("")
async def list_prescription_indicators(
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    rows = (await session.execute(select(PrescriptionIndicatorOrm))).scalars().all()
    return [
        {
            "id": str(r.id),
            "prescription_type_id": str(r.prescription_type_id),
            "indicator_code": r.indicator_code,
            "effect_direction": r.effect_direction,
        }
        for r in rows
    ]
