from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.user_dto import LoginDto, UserMeDto


class UserUseCase(ABC):
    @abstractmethod
    async def login(self, org_id: str, password: str) -> LoginDto:
        ...

    @abstractmethod
    async def get_me(self, user_claims: dict) -> UserMeDto:
        ...
