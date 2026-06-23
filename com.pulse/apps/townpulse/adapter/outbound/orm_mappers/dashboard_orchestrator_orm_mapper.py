from __future__ import annotations

from apps.townpulse.domain.entities.dashboard_orchestrator_entity import DashboardOrchestratorEntity


class DashboardOrchestratorOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> DashboardOrchestratorEntity:
        return DashboardOrchestratorEntity(id=orm_obj.id)
