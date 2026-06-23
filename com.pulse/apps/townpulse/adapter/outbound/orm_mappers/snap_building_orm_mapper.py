from __future__ import annotations

from apps.townpulse.domain.entities.snap_building_entity import SnapBuildingEntity


class SnapBuildingOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> SnapBuildingEntity:
        return SnapBuildingEntity(id=orm_obj.id)
