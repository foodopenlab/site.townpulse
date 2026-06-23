from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.village_detail_orchestrator_dto import VillageDetailDto


class VillageDetailOrchestratorUseCase(ABC):
    @abstractmethod
    async def get_village_detail(self, village_code: str) -> VillageDetailDto | None:
        ...
