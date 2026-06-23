from __future__ import annotations

from apps.townpulse.app.dtos.user_dto import LoginDto, UserMeDto
from apps.townpulse.app.ports.input.user_use_case import UserUseCase
from apps.townpulse.app.ports.output.user_port import UserPort
from core.matrix.grid_trinity_hacker_mixin import DEMO_SCOPE


class UserInteractor(UserUseCase):
    def __init__(self, port: UserPort) -> None:
        self._port = port

    async def login(self, org_id: str, password: str) -> LoginDto:
        return await self._port.authenticate(org_id, password)

    async def get_me(self, user_claims: dict) -> UserMeDto:
        return UserMeDto(
            user_id=user_claims.get("sub", ""),
            org_id=user_claims.get("org_id", ""),
            user_name=user_claims.get("sub", "demo"),
            role="demo" if user_claims.get("scope") == DEMO_SCOPE else "admin",
        )
