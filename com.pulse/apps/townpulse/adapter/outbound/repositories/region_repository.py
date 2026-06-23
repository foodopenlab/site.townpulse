from __future__ import annotations

import logging
from collections import Counter
from datetime import date
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import RegionOrm, SnapPopulationOrm, VillageOrm
from apps.townpulse.app.ports.output.region_port import RegionPort
from apps.townpulse.domain.entities.region_entity import RegionEntity
from apps.townpulse.adapter.outbound.orm_mappers.region_orm_mapper import RegionOrmMapper
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_public_api_client import FISCAL_SELF_RLT_URL, extract_response_items, fetch_json

logger = logging.getLogger(__name__)


class RegionRepository(RegionPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> RegionEntity | None:
        row = await self._session.get(RegionOrm, entity_id)
        return RegionOrmMapper.to_entity(row) if row else None

    async def find_all(self) -> list[RegionEntity]:
        rows = (await self._session.execute(select(RegionOrm).order_by(RegionOrm.sigungu, RegionOrm.emd_name))).scalars().all()
        return [RegionOrmMapper.to_entity(r) for r in rows]

    async def find_by_emd_code(self, emd_code: str) -> RegionEntity | None:
        from sqlalchemy import or_

        stmt = select(RegionOrm).where(
            or_(RegionOrm.legal_dong_code == emd_code, RegionOrm.emd_code == emd_code)
        )
        row = (await self._session.execute(stmt)).scalar_one_or_none()
        return RegionOrmMapper.to_entity(row) if row else None

    async def find_all_legal_dong_codes(self) -> list[str]:
        rows = (await self._session.execute(select(RegionOrm.legal_dong_code))).scalars().all()
        return list(rows)

    async def ingest_fiscal_self_reliance(self) -> None:
        api_key = get_keymaker().get_secret("FISCAL_RELIANCE_API_KEY")
        if not api_key:
            return

        regions = (await self._session.execute(select(RegionOrm))).scalars().all()
        for region in regions:
            value = await self._fetch_fiscal_rate(region.sigungu, api_key)
            if value is not None:
                region.fiscal_self_reliance = value
                region.fiscal_data_year = date.today().replace(month=1, day=1)
        await self._session.flush()

    async def _fetch_fiscal_rate(self, sigungu: str, api_key: str) -> float | None:
        try:
            body = await fetch_json(
                FISCAL_SELF_RLT_URL,
                {
                    "serviceKey": api_key,
                    "type": "json",
                    "numOfRows": 300,
                    "pageNo": 1,
                    "locgovNm": "충청북도",
                },
            )
            rows = extract_response_items(body)
            for row in rows:
                name = str(row.get("locgovNm") or row.get("wafrSelfRltRateNm") or row.get("sggNm") or "")
                if sigungu in name or name in sigungu:
                    raw = row.get("wafrSelfRltRate") or row.get("fncSelfRltRate") or row.get("selfRltRate")
                    if raw is not None:
                        return float(raw)
        except Exception as exc:
            logger.warning("fiscal_api_failed sigungu=%s err=%s", sigungu, exc)
        return None
