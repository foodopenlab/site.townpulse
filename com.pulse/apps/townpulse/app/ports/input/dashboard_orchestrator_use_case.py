from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.dashboard_orchestrator_dto import (
    DashboardSummaryDto,
    VillageListItemDto,
    VillageMapSummaryDto,
)


class DashboardOrchestratorUseCase(ABC):
    @abstractmethod
    async def get_summary(self) -> DashboardSummaryDto:
        ...

    @abstractmethod
    async def get_map_villages(self, grade: str | None, sigun: str | None) -> list[VillageListItemDto]:
        ...

    @abstractmethod
    async def get_village_summary_card(self, village_code: str) -> VillageMapSummaryDto | None:
        ...
