from __future__ import annotations

import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import ReportOrm, TviScoreOrm, VillageOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser, WriteUser

report_router = APIRouter(prefix="/reports", tags=["report"])


class ReportCreateRequest(BaseModel):
    village_id: str
    title: str | None = None
    format: str = "pdf"


@report_router.post("")
async def create_report(
    body: ReportCreateRequest,
    user: WriteUser,
    session: AsyncSession = Depends(get_db),
):
    village = (
        await session.execute(select(VillageOrm).where(VillageOrm.id == UUID(body.village_id)))
    ).scalar_one_or_none()
    if not village:
        raise HTTPException(status_code=404, detail="마을을 찾을 수 없습니다.")

    tvi = (
        await session.execute(
            select(TviScoreOrm)
            .where(TviScoreOrm.village_id == village.id)
            .order_by(desc(TviScoreOrm.calculated_at))
            .limit(1)
        )
    ).scalar_one_or_none()
    if not tvi:
        raise HTTPException(status_code=400, detail="TVI 데이터가 없습니다.")

    user_sub = user.get("sub", "")
    try:
        user_id = UUID(user_sub)
    except ValueError:
        user_id = uuid.uuid4()

    report = ReportOrm(
        id=uuid.uuid4(),
        user_id=user_id,
        village_id=village.id,
        tvi_score_id=tvi.id,
        title=body.title or f"{village.name} 마을생존 리포트",
        format=body.format,
    )
    session.add(report)
    await session.flush()
    return _to_response(report)


@report_router.get("/by-village/{village_id}")
async def list_reports_by_village(
    village_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    rows = (
        await session.execute(
            select(ReportOrm)
            .where(ReportOrm.village_id == UUID(village_id))
            .order_by(desc(ReportOrm.generated_at))
        )
    ).scalars().all()
    return [_to_response(r) for r in rows]


def _to_response(row: ReportOrm) -> dict:
    return {
        "id": str(row.id),
        "user_id": str(row.user_id),
        "village_id": str(row.village_id),
        "tvi_score_id": str(row.tvi_score_id),
        "title": row.title,
        "format": row.format,
        "file_url": row.file_url,
        "generated_at": row.generated_at.isoformat() if row.generated_at else None,
    }
