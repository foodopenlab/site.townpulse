from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.report_orchestrator_dto import ReportBuildQueryDto, ReportDataDto


class ReportOrchestratorUseCase(ABC):
    @abstractmethod
    async def build_report_data(self, village_code: str, query: ReportBuildQueryDto, user_claims: dict) -> ReportDataDto | None:
        ...
