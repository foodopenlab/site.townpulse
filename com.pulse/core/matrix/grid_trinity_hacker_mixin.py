from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.matrix.grid_keymaker_secret_manager import get_keymaker

_bearer = HTTPBearer(auto_error=False)

DEMO_SCOPE = "demo_readonly"
DEMO_TOKEN_TTL_HOURS = 2


def create_access_token(user_id: str, org_id: str, scope: str | None = None) -> str:
    secret = get_keymaker().get_secret("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET이 설정되지 않았습니다.")
    payload: dict[str, Any] = {
        "sub": user_id,
        "org_id": org_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    if scope:
        payload["scope"] = scope
    return jwt.encode(payload, secret, algorithm="HS256")


def create_demo_token() -> str:
    secret = get_keymaker().get_secret("JWT_SECRET")
    payload = {
        "sub": "demo-guest",
        "org_id": "demo",
        "scope": DEMO_SCOPE,
        "exp": datetime.now(timezone.utc) + timedelta(hours=DEMO_TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str) -> dict:
    secret = get_keymaker().get_secret("JWT_SECRET")
    return jwt.decode(token, secret, algorithms=["HS256"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 필요")
    try:
        return verify_token(credentials.credentials)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰") from exc


async def verify_sse_token(token: str = Query(...)) -> dict:
    try:
        return verify_token(token)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 SSE 토큰") from exc


async def require_write_scope(user: dict = Depends(get_current_user)) -> dict:
    if user.get("scope") == DEMO_SCOPE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="데모 모드는 읽기 전용입니다.",
        )
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]
WriteUser = Annotated[dict, Depends(require_write_scope)]
