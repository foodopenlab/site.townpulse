from __future__ import annotations

from apps.townpulse.domain.entities.report_orchestrator_entity import ReportOrchestratorEntity


class ReportOrchestratorOrmMapper:
    @staticmethod
    def to_entity(orm_obj) -> ReportOrchestratorEntity:
        return ReportOrchestratorEntity(id=orm_obj.id)
