from __future__ import annotations

import uuid

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import OrganizationOrm, UserOrm
from apps.townpulse.app.dtos.user_dto import LoginDto
from apps.townpulse.app.ports.output.user_port import UserPort
from apps.townpulse.services.seed_data import MVP_QA_LOGIN_ID, MVP_QA_ORG_UUID


def _resolve_org_uuid(org_id: str) -> uuid.UUID:
    if org_id.strip() == MVP_QA_LOGIN_ID:
        return MVP_QA_ORG_UUID
    return uuid.UUID(org_id)


class UserRepository(UserPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def authenticate(self, org_id: str, password: str) -> LoginDto:
        try:
            org_uuid = _resolve_org_uuid(org_id)
        except ValueError as exc:
            raise ValueError("기관을 찾을 수 없습니다.") from exc
        org = (
            await self._session.execute(
                select(OrganizationOrm).where(OrganizationOrm.id == org_uuid)
            )
        ).scalar_one_or_none()
        if not org:
            raise ValueError("기관을 찾을 수 없습니다.")
        user = (
            await self._session.execute(select(UserOrm).where(UserOrm.organization_id == org.id))
        ).scalar_one_or_none()
        if not user or not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            raise ValueError("비밀번호가 올바르지 않습니다.")
        return LoginDto(
            user_id=str(user.id),
            org_id=str(org.id),
            org_name=org.name,
            user_name=user.name or user.email,
        )
