from __future__ import annotations

from apps.townpulse.domain.entities.user_entity import UserEntity


class UserOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> UserEntity:
        return UserEntity(id=orm_obj.id)
