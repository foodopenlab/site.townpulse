from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.village_schema import VillageDetailResponse, VillageListItemResponse
from apps.townpulse.app.dtos.village_dto import VillageDto


class VillageMapper:
    @staticmethod
    def to_list_item(dto: VillageDto) -> VillageListItemResponse:
        return VillageListItemResponse(id=str(dto.id), emd_code=dto.emd_code, name=dto.name)

    @staticmethod
    def to_detail_response(dto: VillageDto) -> VillageDetailResponse:
        return VillageDetailResponse(
            id=str(dto.id),
            emd_code=dto.emd_code,
            name=dto.name,
            region_id=str(dto.region_id) if dto.region_id else None,
            lat=dto.lat,
            lng=dto.lng,
            last_synced_at=dto.last_synced_at,
            sigungu=dto.sigungu,
        )
