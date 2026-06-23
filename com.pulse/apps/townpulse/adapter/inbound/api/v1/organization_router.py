from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import OrganizationOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

organization_router = APIRouter(prefix="/organizations", tags=["organization"])


@organization_router.get("/{org_id}")
async def get_organization(
    org_id: str,
    _user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    org = (
        await session.execute(select(OrganizationOrm).where(OrganizationOrm.id == UUID(org_id)))
    ).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="기관을 찾을 수 없습니다.")
    return {
        "id": str(org.id),
        "name": org.name,
        "org_type": org.org_type,
        "region_code": org.region_code,
        "created_at": org.created_at.isoformat() if org.created_at else None,
    }
