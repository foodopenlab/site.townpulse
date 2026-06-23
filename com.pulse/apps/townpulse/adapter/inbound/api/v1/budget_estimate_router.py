from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import (
    BudgetEstimateOrm,
    BudgetUnitPriceOrm,
    PrescriptionResultOrm,
)
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser, WriteUser

budget_estimate_router = APIRouter(prefix="/budget-estimates", tags=["budget_estimate"])


class BudgetEstimateCreateRequest(BaseModel):
    prescription_result_id: str
    quantity: int = Field(default=1, ge=1)


@budget_estimate_router.post("")
async def create_budget_estimate(
    body: BudgetEstimateCreateRequest,
    _user: WriteUser,
    session: AsyncSession = Depends(get_db),
):
    result = (
        await session.execute(
            select(PrescriptionResultOrm).where(
                PrescriptionResultOrm.id == UUID(body.prescription_result_id)
            )
        )
    ).scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="처방 결과를 찾을 수 없습니다.")

    existing = (
        await session.execute(
            select(BudgetEstimateOrm).where(
                BudgetEstimateOrm.prescription_result_id == result.id
            )
        )
    ).scalar_one_or_none()
    if existing:
        return _to_response(existing)

    price = (
        await session.execute(
            select(BudgetUnitPriceOrm).where(
                BudgetUnitPriceOrm.prescription_type_id == result.prescription_type_id
            )
        )
    ).scalar_one_or_none()
    if not price:
        raise HTTPException(status_code=400, detail="예산 단가가 없습니다.")

    estimate = BudgetEstimateOrm(
        id=uuid.uuid4(),
        prescription_result_id=result.id,
        budget_unit_price_id=price.id,
        quantity=body.quantity,
        budget_min=price.price_min * body.quantity,
        budget_max=price.price_max * body.quantity,
        calculation_note="API 산출",
    )
    session.add(estimate)
    await session.flush()
    return _to_response(estimate)


@budget_estimate_router.get("/by-prescription/{prescription_result_id}")
async def get_budget_by_prescription(
    prescription_result_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    row = (
        await session.execute(
            select(BudgetEstimateOrm).where(
                BudgetEstimateOrm.prescription_result_id == UUID(prescription_result_id)
            )
        )
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="예산 산출이 없습니다.")
    return _to_response(row)


def _to_response(row: BudgetEstimateOrm) -> dict:
    return {
        "id": str(row.id),
        "prescription_result_id": str(row.prescription_result_id),
        "budget_unit_price_id": str(row.budget_unit_price_id),
        "quantity": row.quantity,
        "budget_min": row.budget_min,
        "budget_max": row.budget_max,
        "calculation_note": row.calculation_note,
    }
