from __future__ import annotations

from apps.townpulse.domain.entities.public_data_sync_orchestrator_entity import PublicDataSyncOrchestratorEntity


class PublicDataSyncOrchestratorOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> PublicDataSyncOrchestratorEntity:
        return PublicDataSyncOrchestratorEntity(id=orm_obj.id)
