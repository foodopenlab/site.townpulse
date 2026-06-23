from __future__ import annotations

from apps.townpulse.domain.entities.prescription_result_entity import PrescriptionResultEntity


class PrescriptionResultOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> PrescriptionResultEntity:
        return PrescriptionResultEntity(id=orm_obj.id)
