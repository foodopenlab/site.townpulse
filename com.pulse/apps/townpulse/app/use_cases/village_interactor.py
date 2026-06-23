from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.village_dto import VillageDto, VillageListResult
from apps.townpulse.app.ports.input.village_use_case import VillageUseCase
from apps.townpulse.app.ports.output.village_port import VillagePort
from apps.townpulse.domain.entities.village_entity import VillageEntity


class VillageInteractor(VillageUseCase):
    def __init__(self, port: VillagePort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> VillageDto | None:
        entity = await self._port.find_by_id(entity_id)
        return self._to_dto(entity) if entity else None

    async def find_all(self) -> VillageListResult:
        entities = await self._port.find_all()
        items = [self._to_dto(e) for e in entities]
        return VillageListResult(items=items, total=len(items))

    async def find_by_code(self, emd_code: str) -> VillageDto | None:
        entity = await self._port.find_by_code(emd_code)
        return self._to_dto(entity) if entity else None

    async def find_by_region(self, region_id: UUID) -> VillageListResult:
        entities = await self._port.find_by_region(region_id)
        items = [self._to_dto(e) for e in entities]
        return VillageListResult(items=items, total=len(items))

    @staticmethod
    def _to_dto(entity: VillageEntity) -> VillageDto:
        return VillageDto(
            id=entity.id,
            emd_code=entity.emd_code,
            name=entity.name,
            region_id=entity.region_id,
            lat=entity.lat,
            lng=entity.lng,
            last_synced_at=entity.last_synced_at,
            sigungu=entity.sigungu,
        )
