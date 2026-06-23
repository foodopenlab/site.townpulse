from __future__ import annotations

from apps.townpulse.adapter.outbound.orm.region_orm import RegionOrm
from apps.townpulse.domain.entities.region_entity import RegionEntity


class RegionOrmMapper:
    @staticmethod
    def to_entity(orm_obj: RegionOrm) -> RegionEntity:
        return RegionEntity(
            id=orm_obj.id,
            sido=orm_obj.sido,
            sigungu=orm_obj.sigungu,
            emd_name=orm_obj.emd_name,
            legal_dong_code=orm_obj.legal_dong_code,
            sigungu_code=orm_obj.sigungu_code,
            emd_code=orm_obj.emd_code,
            tago_city_code=orm_obj.tago_city_code,
            area_km2=orm_obj.area_km2,
            fiscal_self_reliance=orm_obj.fiscal_self_reliance,
            fiscal_data_year=orm_obj.fiscal_data_year,
            birth_rate=orm_obj.birth_rate,
            daytime_population=orm_obj.daytime_population,
            demographic_data_year=orm_obj.demographic_data_year,
        )
