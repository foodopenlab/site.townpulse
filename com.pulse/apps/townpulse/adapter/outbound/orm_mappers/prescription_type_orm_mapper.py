from __future__ import annotations

from apps.townpulse.adapter.outbound.orm.prescription_type_orm import PrescriptionTypeOrm
from apps.townpulse.domain.entities.prescription_type_entity import PrescriptionTypeEntity


class PrescriptionTypeOrmMapper:
    @staticmethod
    def to_entity(orm_obj: PrescriptionTypeOrm) -> PrescriptionTypeEntity:
        return PrescriptionTypeEntity(
            id=orm_obj.id,
            code=orm_obj.code,
            name=orm_obj.name,
            category=orm_obj.category,
            rollout_timeline=orm_obj.rollout_timeline,
            is_active=orm_obj.is_active,
        )
