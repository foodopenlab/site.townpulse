from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import DispatchRuleOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

dispatch_rule_router = APIRouter(prefix="/dispatch-rules", tags=["dispatch_rule"])


@dispatch_rule_router.get("")
async def list_dispatch_rules(
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    rows = (
        await session.execute(select(DispatchRuleOrm).order_by(DispatchRuleOrm.priority_rank))
    ).scalars().all()
    return [
        {
            "id": str(r.id),
            "prescription_type_id": str(r.prescription_type_id),
            "trigger_indicator": r.trigger_indicator,
            "operator": r.operator,
            "threshold_value": r.threshold_value,
            "priority_rank": r.priority_rank,
        }
        for r in rows
    ]
