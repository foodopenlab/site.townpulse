from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from apps.townpulse.adapter.inbound.api.schemas.user_schema import (
    DemoTokenResponse,
    LoginRequest,
    LoginResponse,
    UserMeResponse,
)
from apps.townpulse.adapter.inbound.mappers.user_mapper import UserMapper
from apps.townpulse.app.ports.input.user_use_case import UserUseCase
from apps.townpulse.dependencies.user_provider import get_user_use_case
from core.matrix.grid_trinity_hacker_mixin import (
    DEMO_SCOPE,
    DEMO_TOKEN_TTL_HOURS,
    CurrentUser,
    create_access_token,
    create_demo_token,
)

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.post("/login", response_model=LoginResponse)
async def user_login(body: LoginRequest, use_case: UserUseCase = Depends(get_user_use_case)):
    try:
        dto = await use_case.login(body.org_id, body.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    token = create_access_token(dto.user_id, dto.org_id)
    return UserMapper.to_login_response(dto, token)


@user_router.post("/demo/token", response_model=DemoTokenResponse)
async def demo_token():
    return DemoTokenResponse(
        access_token=create_demo_token(),
        scope=DEMO_SCOPE,
        expires_in=DEMO_TOKEN_TTL_HOURS * 3600,
    )


@user_router.get("/me", response_model=UserMeResponse)
async def user_me(user: CurrentUser, use_case: UserUseCase = Depends(get_user_use_case)):
    return UserMapper.to_me_response(await use_case.get_me(user))
