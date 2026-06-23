from __future__ import annotations

from apps.townpulse.app.dtos.village_detail_orchestrator_dto import VillageDetailDto
from apps.townpulse.app.ports.input.village_detail_orchestrator_use_case import VillageDetailOrchestratorUseCase
from apps.townpulse.app.ports.output.village_detail_orchestrator_port import VillageDetailOrchestratorPort
from core.matrix.grid_morpheus_base_orchestrator import MorpheusOrchestratorBase


class VillageDetailOrchestratorInteractor(VillageDetailOrchestratorUseCase, MorpheusOrchestratorBase):
    def __init__(self, port: VillageDetailOrchestratorPort) -> None:
        self._port = port

    async def get_village_detail(self, village_code: str) -> VillageDetailDto | None:
        return await self._port.fetch_village_detail(village_code)
