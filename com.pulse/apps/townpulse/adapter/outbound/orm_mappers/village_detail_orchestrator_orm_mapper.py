from __future__ import annotations

from apps.townpulse.domain.entities.village_detail_orchestrator_entity import VillageDetailOrchestratorEntity


class VillageDetailOrchestratorOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> VillageDetailOrchestratorEntity:
        return VillageDetailOrchestratorEntity(id=orm_obj.id)
