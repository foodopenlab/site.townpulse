from __future__ import annotations

from apps.townpulse.domain.entities.prescription_indicator_entity import PrescriptionIndicatorEntity


class PrescriptionIndicatorOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> PrescriptionIndicatorEntity:
        return PrescriptionIndicatorEntity(id=orm_obj.id)
