from __future__ import annotations

from apps.townpulse.app.dtos.report_orchestrator_dto import ReportBuildQueryDto, ReportDataDto
from apps.townpulse.app.ports.input.report_orchestrator_use_case import ReportOrchestratorUseCase
from apps.townpulse.app.ports.output.report_orchestrator_port import ReportOrchestratorPort
from core.matrix.grid_morpheus_base_orchestrator import MorpheusOrchestratorBase


class ReportOrchestratorInteractor(ReportOrchestratorUseCase, MorpheusOrchestratorBase):
    def __init__(self, port: ReportOrchestratorPort) -> None:
        self._port = port

    async def build_report_data(
        self, village_code: str, query: ReportBuildQueryDto, user_claims: dict
    ) -> ReportDataDto | None:
        return await self._port.build_report_data(village_code, query, user_claims)
