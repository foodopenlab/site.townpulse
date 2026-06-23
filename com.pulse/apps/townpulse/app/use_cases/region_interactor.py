from __future__ import annotations

from uuid import UUID

from apps.townpulse.app.dtos.region_dto import RegionDto, RegionListResult
from apps.townpulse.app.ports.input.region_use_case import RegionUseCase
from apps.townpulse.app.ports.output.region_port import RegionPort
from apps.townpulse.domain.entities.region_entity import RegionEntity


class RegionInteractor(RegionUseCase):
    def __init__(self, port: RegionPort) -> None:
        self._port = port

    async def find_by_id(self, entity_id: UUID) -> RegionDto | None:
        entity = await self._port.find_by_id(entity_id)
        return self._to_dto(entity) if entity else None

    async def find_all(self) -> RegionListResult:
        entities = await self._port.find_all()
        items = [self._to_dto(e) for e in entities]
        return RegionListResult(items=items, total=len(items))

    async def find_by_emd_code(self, emd_code: str) -> RegionDto | None:
        entity = await self._port.find_by_emd_code(emd_code)
        return self._to_dto(entity) if entity else None

    @staticmethod
    def _to_dto(entity: RegionEntity) -> RegionDto:
        return RegionDto(
            id=entity.id,
            sigungu=entity.sigungu,
            legal_dong_code=entity.legal_dong_code,
            sido=entity.sido,
            emd_name=entity.emd_name,
            emd_code=entity.emd_code,
            sigungu_code=entity.sigungu_code,
            tago_city_code=entity.tago_city_code,
            area_km2=entity.area_km2,
            fiscal_self_reliance=entity.fiscal_self_reliance,
            fiscal_data_year=entity.fiscal_data_year,
            birth_rate=entity.birth_rate,
            daytime_population=entity.daytime_population,
            demographic_data_year=entity.demographic_data_year,
        )
