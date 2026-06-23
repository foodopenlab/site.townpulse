from __future__ import annotations

from apps.townpulse.adapter.outbound.orm.village_orm import VillageOrm
from apps.townpulse.domain.entities.village_entity import VillageEntity


class VillageOrmMapper:
    @staticmethod
    def to_entity(orm_obj: VillageOrm, sigungu: str | None = None) -> VillageEntity:
        region_sigungu = sigungu
        region_sigungu_code = None
        region = orm_obj.__dict__.get("region") or getattr(orm_obj, "region", None)
        if region is not None:
            if region_sigungu is None:
                region_sigungu = region.sigungu
            region_sigungu_code = region.sigungu_code
        return VillageEntity(
            id=orm_obj.id,
            region_id=orm_obj.region_id,
            name=orm_obj.name,
            emd_code=orm_obj.emd_code,
            lat=orm_obj.lat,
            lng=orm_obj.lng,
            last_synced_at=orm_obj.last_synced_at,
            sigungu=region_sigungu,
            sigungu_code=region_sigungu_code,
        )
