from __future__ import annotations

from dataclasses import asdict

from apps.townpulse.adapter.inbound.api.schemas.dashboard_orchestrator_schema import (
    DashboardSummaryResponse,
    VillageListItemResponse,
    VillageMapSummaryResponse,
)
from apps.townpulse.app.dtos.dashboard_orchestrator_dto import (
    DashboardSummaryDto,
    VillageListItemDto,
    VillageMapSummaryDto,
)


class DashboardOrchestratorMapper:
    @staticmethod
    def to_summary_response(dto: DashboardSummaryDto) -> DashboardSummaryResponse:
        return DashboardSummaryResponse(**asdict(dto))

    @staticmethod
    def to_village_list_item(dto: VillageListItemDto) -> VillageListItemResponse:
        return VillageListItemResponse(**asdict(dto))

    @staticmethod
    def to_map_summary(dto: VillageMapSummaryDto) -> VillageMapSummaryResponse:
        return VillageMapSummaryResponse(**asdict(dto))
