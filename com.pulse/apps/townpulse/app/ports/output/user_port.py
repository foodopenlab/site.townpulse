from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.user_dto import LoginDto


class UserPort(ABC):
    @abstractmethod
    async def authenticate(self, org_id: str, password: str) -> LoginDto:
        ...
