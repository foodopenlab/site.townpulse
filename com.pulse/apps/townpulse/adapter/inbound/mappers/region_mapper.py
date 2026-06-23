from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.region_schema import RegionDetailResponse, RegionListItemResponse
from apps.townpulse.app.dtos.region_dto import RegionDto


class RegionMapper:
    @staticmethod
    def to_list_item(dto: RegionDto) -> RegionListItemResponse:
        return RegionListItemResponse(
            id=str(dto.id),
            sigungu=dto.sigungu,
            legal_dong_code=dto.legal_dong_code,
        )

    @staticmethod
    def to_detail_response(dto: RegionDto) -> RegionDetailResponse:
        return RegionDetailResponse(
            id=str(dto.id),
            sido=dto.sido or "",
            sigungu=dto.sigungu,
            emd_name=dto.emd_name or "",
            legal_dong_code=dto.legal_dong_code,
            emd_code=dto.emd_code,
            sigungu_code=dto.sigungu_code,
            tago_city_code=dto.tago_city_code,
            area_km2=dto.area_km2,
            fiscal_self_reliance=dto.fiscal_self_reliance,
            fiscal_data_year=dto.fiscal_data_year,
            birth_rate=dto.birth_rate,
            daytime_population=dto.daytime_population,
            demographic_data_year=dto.demographic_data_year,
        )
