from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.dashboard_orchestrator_dto import (
    DashboardSummaryDto,
    VillageListItemDto,
    VillageMapSummaryDto,
)


class DashboardOrchestratorPort(ABC):
    @abstractmethod
    async def fetch_summary(self) -> DashboardSummaryDto:
        ...

    @abstractmethod
    async def fetch_map_villages(self, grade: str | None, sigun: str | None) -> list[VillageListItemDto]:
        ...

    @abstractmethod
    async def fetch_village_summary_card(self, village_code: str) -> VillageMapSummaryDto | None:
        ...
