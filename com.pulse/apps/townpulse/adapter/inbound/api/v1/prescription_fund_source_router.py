from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import PrescriptionFundSourceOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

prescription_fund_source_router = APIRouter(
    prefix="/prescription-fund-sources", tags=["prescription_fund_source"]
)


@prescription_fund_source_router.get("")
async def list_prescription_fund_sources(
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    rows = (await session.execute(select(PrescriptionFundSourceOrm))).scalars().all()
    return [
        {
            "id": str(r.id),
            "prescription_type_id": str(r.prescription_type_id),
            "fund_name": r.fund_name,
            "fund_org": r.fund_org,
            "is_eligible": r.is_eligible,
        }
        for r in rows
    ]
