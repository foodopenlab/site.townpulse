from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.user_schema import LoginResponse, UserMeResponse
from apps.townpulse.app.dtos.user_dto import LoginDto, UserMeDto


class UserMapper:
    @staticmethod
    def to_login_response(dto: LoginDto, access_token: str) -> LoginResponse:
        return LoginResponse(
            access_token=access_token,
            org_name=dto.org_name,
            user_name=dto.user_name,
        )

    @staticmethod
    def to_me_response(dto: UserMeDto) -> UserMeResponse:
        return UserMeResponse(
            user_id=dto.user_id,
            org_id=dto.org_id,
            user_name=dto.user_name,
            role=dto.role,
        )
