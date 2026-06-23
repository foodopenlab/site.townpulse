from __future__ import annotations

from apps.townpulse.domain.entities.snap_transport_entity import SnapTransportEntity


class SnapTransportOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> SnapTransportEntity:
        return SnapTransportEntity(id=orm_obj.id)
