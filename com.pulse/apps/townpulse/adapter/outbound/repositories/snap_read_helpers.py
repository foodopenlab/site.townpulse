"""SNAP 조회 공통 헬퍼."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession


def _serialize_row(row: Any, fields: tuple[str, ...]) -> dict:
    out: dict[str, Any] = {"id": str(row.id), "village_id": str(row.village_id)}
    for field in fields:
        value = getattr(row, field)
        if isinstance(value, (date, datetime)):
            out[field] = value.isoformat()
        else:
            out[field] = value
    return out


async def find_latest(
    session: AsyncSession,
    model: type,
    village_id: UUID,
    fields: tuple[str, ...],
) -> dict | None:
    row = (
        await session.execute(
            select(model)
            .where(model.village_id == village_id)
            .order_by(desc(model.snapshot_date))
            .limit(1)
        )
    ).scalar_one_or_none()
    if not row:
        return None
    return _serialize_row(row, fields)


async def find_history(
    session: AsyncSession,
    model: type,
    village_id: UUID,
    fields: tuple[str, ...],
    limit: int = 12,
) -> list[dict]:
    rows = (
        await session.execute(
            select(model)
            .where(model.village_id == village_id)
            .order_by(desc(model.snapshot_date))
            .limit(limit)
        )
    ).scalars().all()
    return [_serialize_row(r, fields) for r in rows]
