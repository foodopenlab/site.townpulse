from __future__ import annotations

from apps.townpulse.domain.entities.organization_entity import OrganizationEntity


class OrganizationOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> OrganizationEntity:
        return OrganizationEntity(id=orm_obj.id)
