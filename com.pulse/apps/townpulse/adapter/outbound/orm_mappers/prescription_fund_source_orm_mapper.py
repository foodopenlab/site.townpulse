from __future__ import annotations

from apps.townpulse.domain.entities.prescription_fund_source_entity import PrescriptionFundSourceEntity


class PrescriptionFundSourceOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> PrescriptionFundSourceEntity:
        return PrescriptionFundSourceEntity(id=orm_obj.id)
