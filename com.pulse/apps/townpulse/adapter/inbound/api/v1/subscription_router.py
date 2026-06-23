from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SubscriptionOrm
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

subscription_router = APIRouter(prefix="/subscriptions", tags=["subscription"])


@subscription_router.get("/my")
async def get_my_subscription(
    user: CurrentUser,
    session: AsyncSession = Depends(get_db),
):
    org_id = user.get("org_id")
    if not org_id:
        raise HTTPException(status_code=404, detail="구독 정보가 없습니다.")
    try:
        org_uuid = UUID(org_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="구독 정보가 없습니다.") from None

    sub = (
        await session.execute(
            select(SubscriptionOrm)
            .where(SubscriptionOrm.organization_id == org_uuid)
            .order_by(SubscriptionOrm.started_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="구독 정보가 없습니다.")
    return {
        "id": str(sub.id),
        "organization_id": str(sub.organization_id),
        "tier": sub.tier,
        "started_at": sub.started_at.isoformat(),
        "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        "is_active": sub.is_active,
        "monthly_fee": sub.monthly_fee,
    }
