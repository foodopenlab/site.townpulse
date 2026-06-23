from __future__ import annotations

from apps.townpulse.domain.entities.report_entity import ReportEntity


class ReportOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> ReportEntity:
        return ReportEntity(id=orm_obj.id)
