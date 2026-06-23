from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LoginDto:
    user_id: str
    org_id: str
    org_name: str
    user_name: str


@dataclass(slots=True)
class UserMeDto:
    user_id: str
    org_id: str
    user_name: str
    role: str
