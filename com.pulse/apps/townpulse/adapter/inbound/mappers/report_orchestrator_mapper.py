from __future__ import annotations

from dataclasses import asdict

from apps.townpulse.adapter.inbound.api.schemas.report_orchestrator_schema import ReportDataResponse
from apps.townpulse.app.dtos.report_orchestrator_dto import ReportBuildQueryDto, ReportDataDto


class ReportOrchestratorMapper:
    @staticmethod
    def to_query(body) -> ReportBuildQueryDto:
        return ReportBuildQueryDto(
            include_risk_analysis=body.include_risk_analysis,
            include_prescriptions=body.include_prescriptions,
            include_budget=body.include_budget,
            include_map_snapshot=body.include_map_snapshot,
        )

    @staticmethod
    def to_response(dto: ReportDataDto) -> ReportDataResponse:
        return ReportDataResponse(**asdict(dto))
