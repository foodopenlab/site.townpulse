from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.village_detail_orchestrator_dto import VillageDetailDto


class VillageDetailOrchestratorPort(ABC):
    @abstractmethod
    async def fetch_village_detail(self, village_code: str) -> VillageDetailDto | None:
        ...
