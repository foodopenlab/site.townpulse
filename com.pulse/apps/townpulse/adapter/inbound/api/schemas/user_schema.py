from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    org_id: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    org_name: str
    user_name: str


class DemoTokenResponse(BaseModel):
    access_token: str
    scope: str
    expires_in: int


class UserMeResponse(BaseModel):
    user_id: str
    org_id: str
    user_name: str
    role: str
