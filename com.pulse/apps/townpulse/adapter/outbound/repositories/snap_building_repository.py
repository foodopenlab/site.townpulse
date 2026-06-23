from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapBuildingOrm, VillageOrm
from apps.townpulse.app.ports.output.snap_building_port import SnapBuildingPort
from apps.townpulse.domain.entities.snap_building_entity import SnapBuildingEntity
from apps.townpulse.domain.value_objects.residential_purpose_vo import RESIDENTIAL_PURPOSE_NAMES
from apps.townpulse.services.legal_dong_resolver import current_stats_ym
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_public_api_client import BUILDING_HUB_TITLE_URL, fetch_all_pages

logger = logging.getLogger(__name__)


class SnapBuildingRepository(SnapBuildingPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> SnapBuildingEntity | None:
        return None

    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        api_key = get_keymaker().get_secret("BUILDING_HUB_API_KEY")
        if not api_key or len(legal_dong_code) != 10:
            return

        sigungu_cd = legal_dong_code[:5]
        bjdong_cd = legal_dong_code[5:10]
        rows = await self._fetch_all_br_title_pages(sigungu_cd, bjdong_cd, api_key)
        residential_count, unmatched = self._count_residential_with_audit(rows)
        if unmatched:
            self._log_unmatched_purpose_names(legal_dong_code, unmatched)
        await self._upsert_snap_row(legal_dong_code, {"residential_buildings": residential_count})

    async def _fetch_all_br_title_pages(
        self, sigungu_cd: str, bjdong_cd: str, api_key: str
    ) -> list[dict]:
        params = {
            "serviceKey": api_key,
            "sigunguCd": sigungu_cd,
            "bjdongCd": bjdong_cd,
            "_type": "json",
        }
        return await fetch_all_pages(BUILDING_HUB_TITLE_URL, params)

    def _count_residential_with_audit(self, rows: list[dict]) -> tuple[int, dict[str, int]]:
        count = 0
        unmatched: dict[str, int] = {}
        for row in rows:
            raw = (row.get("mainPurpsCdNm") or "").strip()
            if raw in RESIDENTIAL_PURPOSE_NAMES:
                count += 1
            elif raw:
                unmatched[raw] = unmatched.get(raw, 0) + 1
        return count, unmatched

    def _log_unmatched_purpose_names(self, legal_dong_code: str, unmatched: dict[str, int]) -> None:
        logger.warning(
            "residential_classification_unmatched legal_dong_code=%s unmatched=%s",
            legal_dong_code,
            unmatched,
        )

    async def _upsert_snap_row(self, legal_dong_code: str, raw: dict) -> None:
        village = (
            await self._session.execute(select(VillageOrm).where(VillageOrm.emd_code == legal_dong_code))
        ).scalar_one_or_none()
        if not village:
            return

        stats_ym = current_stats_ym()
        snapshot_date = date(int(stats_ym[:4]), int(stats_ym[4:6]), 1)

        existing = (
            await self._session.execute(
                select(SnapBuildingOrm)
                .where(SnapBuildingOrm.village_id == village.id)
                .order_by(desc(SnapBuildingOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()

        value = raw.get("residential_buildings")
        if existing:
            if value is not None:
                existing.residential_buildings = value
            existing.snapshot_date = snapshot_date
        else:
            self._session.add(
                SnapBuildingOrm(
                    village_id=village.id,
                    snapshot_date=snapshot_date,
                    residential_buildings=value,
                )
            )
        await self._session.flush()
