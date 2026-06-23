from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import BudgetUnitPriceOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

budget_unit_price_router = APIRouter(prefix="/budget-unit-prices", tags=["budget_unit_price"])


@budget_unit_price_router.get("")
async def list_budget_unit_prices(
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    rows = (await session.execute(select(BudgetUnitPriceOrm))).scalars().all()
    return [
        {
            "id": str(r.id),
            "prescription_type_id": str(r.prescription_type_id),
            "unit": r.unit,
            "price_min": r.price_min,
            "price_max": r.price_max,
            "reference_source": r.reference_source,
            "effective_from": r.effective_from.isoformat() if r.effective_from else None,
        }
        for r in rows
    ]
