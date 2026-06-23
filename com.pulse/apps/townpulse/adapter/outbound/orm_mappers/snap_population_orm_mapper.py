from __future__ import annotations

from apps.townpulse.domain.entities.snap_population_entity import SnapPopulationEntity


class SnapPopulationOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> SnapPopulationEntity:
        return SnapPopulationEntity(id=orm_obj.id)
