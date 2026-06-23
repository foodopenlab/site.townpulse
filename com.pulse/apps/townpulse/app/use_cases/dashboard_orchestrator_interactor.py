from __future__ import annotations

from apps.townpulse.app.dtos.dashboard_orchestrator_dto import (
    DashboardSummaryDto,
    VillageListItemDto,
    VillageMapSummaryDto,
)
from apps.townpulse.app.ports.input.dashboard_orchestrator_use_case import DashboardOrchestratorUseCase
from apps.townpulse.app.ports.output.dashboard_orchestrator_port import DashboardOrchestratorPort
from core.matrix.grid_morpheus_base_orchestrator import MorpheusOrchestratorBase


class DashboardOrchestratorInteractor(DashboardOrchestratorUseCase, MorpheusOrchestratorBase):
    def __init__(self, port: DashboardOrchestratorPort) -> None:
        self._port = port

    async def get_summary(self) -> DashboardSummaryDto:
        return await self._port.fetch_summary()

    async def get_map_villages(self, grade: str | None, sigun: str | None) -> list[VillageListItemDto]:
        return await self._port.fetch_map_villages(grade, sigun)

    async def get_village_summary_card(self, village_code: str) -> VillageMapSummaryDto | None:
        return await self._port.fetch_village_summary_card(village_code)
