from __future__ import annotations

from apps.townpulse.domain.entities.snap_statistics_entity import SnapStatisticsEntity


class SnapStatisticsOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> SnapStatisticsEntity:
        return SnapStatisticsEntity(id=orm_obj.id)
