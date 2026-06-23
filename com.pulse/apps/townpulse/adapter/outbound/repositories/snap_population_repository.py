from __future__ import annotations

from collections import Counter
from datetime import date
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import SnapPopulationOrm, VillageOrm
from apps.townpulse.app.ports.output.snap_population_port import SnapPopulationPort
from apps.townpulse.domain.entities.snap_population_entity import SnapPopulationEntity
from apps.townpulse.domain.value_objects.sido_code_vo import SIDO_CODES, sido_admm_cd
from apps.townpulse.services.legal_dong_resolver import current_stats_ym
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_public_api_client import (
    MOIS_AGE_URL,
    MOIS_HOUSEHOLD_URL,
    MOIS_MIGRATION_URL,
    extract_single_item,
    fetch_all_pages,
    fetch_json,
)

ELDERLY_DECADES = (70, 80, 90, 100)
YOUTH_DECADES = (20, 30)
MIGRATION_YOUTH_AGES = range(20, 40)


def _sum_migration_youth(item: dict) -> int:
    return sum(
        int(item.get(f"male{age}AgeNmprCnt") or 0) + int(item.get(f"feml{age}AgeNmprCnt") or 0)
        for age in MIGRATION_YOUTH_AGES
    )


def _sum_elderly(item: dict) -> int:
    return sum(
        int(item.get(f"male{age}AgeNmprCnt") or 0) + int(item.get(f"feml{age}AgeNmprCnt") or 0)
        for age in ELDERLY_DECADES
    )


def _sum_youth(item: dict) -> int:
    return sum(
        int(item.get(f"male{age}AgeNmprCnt") or 0) + int(item.get(f"feml{age}AgeNmprCnt") or 0)
        for age in YOUTH_DECADES
    )


def _aggregate_household(rows: list[dict]) -> dict[str, int]:
    return {
        "population_total": sum(int(r.get("totNmprCnt") or 0) for r in rows),
        "registered_households": sum(int(r.get("hhCnt") or 0) for r in rows),
    }


def _aggregate_age(rows: list[dict]) -> dict[str, int]:
    return {
        "population_65plus": sum(_sum_elderly(r) for r in rows),
        "population_youth": sum(_sum_youth(r) for r in rows),
    }


class SnapPopulationRepository(SnapPopulationPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, entity_id: UUID) -> SnapPopulationEntity | None:
        return None

    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        await self.ingest_core_from_public_api(legal_dong_code)

    async def ingest_core_from_public_api(self, legal_dong_code: str) -> None:
        km = get_keymaker()
        household_key = km.get_secret("POPULATION_HOUSEHOLD_API_KEY")
        age_key = km.get_secret("POPULATION_AGE_API_KEY")
        if not household_key or not age_key:
            return
        if len(legal_dong_code) != 10:
            return

        stats_ym = current_stats_ym()
        household_rows = await self._fetch_household_rows(legal_dong_code, stats_ym, household_key)
        age_rows = await self._fetch_age_rows(legal_dong_code, stats_ym, age_key)
        if not household_rows and not age_rows:
            return

        raw = {**_aggregate_household(household_rows), **_aggregate_age(age_rows)}
        await self._upsert_snap_row(legal_dong_code, raw, stats_ym)

    async def ingest_migration_from_public_api(self, legal_dong_code: str) -> None:
        migration_key = get_keymaker().get_secret("POPULATION_MIGRATION_API_KEY")
        household_key = get_keymaker().get_secret("POPULATION_HOUSEHOLD_API_KEY")
        if not migration_key or len(legal_dong_code) != 10:
            return

        stats_ym = current_stats_ym()
        year = int(stats_ym[:4])
        month = int(stats_ym[4:6])
        snapshot_date = date(year, month, 1)

        village = (
            await self._session.execute(select(VillageOrm).where(VillageOrm.emd_code == legal_dong_code))
        ).scalar_one_or_none()
        if not village:
            return

        existing = (
            await self._session.execute(
                select(SnapPopulationOrm)
                .where(SnapPopulationOrm.village_id == village.id)
                .where(SnapPopulationOrm.snapshot_date == snapshot_date)
            )
        ).scalar_one_or_none()

        if existing and existing.net_youth_migration is not None:
            return

        admm_cd = await self._resolve_mvin_admm_cd(legal_dong_code, household_key)
        if not admm_cd:
            return

        net_youth = await self._compute_net_youth_migration(admm_cd, stats_ym, migration_key)
        await self._upsert_snap_row(legal_dong_code, {"net_youth_migration": net_youth}, stats_ym)

    async def _resolve_mvin_admm_cd(self, legal_dong_code: str, household_key: str | None) -> str | None:
        if not household_key:
            return None
        rows = await self._fetch_household_rows(legal_dong_code, current_stats_ym(), household_key)
        counts = Counter(str(r["admmCd"]) for r in rows if r.get("admmCd"))
        return counts.most_common(1)[0][0] if counts else None

    async def _fetch_migration_pair(
        self, mvin_admm_cd: str, mvt_admm_cd: str, stats_ym: str, api_key: str
    ) -> dict:
        body = await fetch_json(
            MOIS_MIGRATION_URL,
            {
                "serviceKey": api_key,
                "mvinAdmmCd": mvin_admm_cd,
                "mvtAdmmCd": mvt_admm_cd,
                "srchFrYm": stats_ym,
                "srchToYm": stats_ym,
                "lv": "3",
                "type": "json",
                "pageNo": 1,
                "numOfRows": 10,
            },
        )
        return extract_single_item(body) or {}

    async def _compute_net_youth_migration(self, admm_cd: str, stats_ym: str, api_key: str) -> int:
        total_in = 0
        for sido in SIDO_CODES:
            raw = await self._fetch_migration_pair(admm_cd, sido_admm_cd(sido), stats_ym, api_key)
            total_in += _sum_migration_youth(raw)
        total_out = 0
        for sido in SIDO_CODES:
            raw = await self._fetch_migration_pair(sido_admm_cd(sido), admm_cd, stats_ym, api_key)
            total_out += _sum_migration_youth(raw)
        return total_in - total_out

    async def _fetch_household_rows(
        self, legal_dong_code: str, stats_ym: str, api_key: str
    ) -> list[dict]:
        params = {
            "serviceKey": api_key,
            "stdgCd": legal_dong_code,
            "srchFrYm": stats_ym,
            "srchToYm": stats_ym,
            "lv": "4",
            "regSeCd": "1",
            "type": "json",
        }
        rows = await fetch_all_pages(MOIS_HOUSEHOLD_URL, params)
        return [r for r in rows if str(r.get("stdgCd", "")).startswith(legal_dong_code[:8])]

    async def _fetch_age_rows(self, legal_dong_code: str, stats_ym: str, api_key: str) -> list[dict]:
        params = {
            "serviceKey": api_key,
            "stdgCd": legal_dong_code,
            "srchFrYm": stats_ym,
            "srchToYm": stats_ym,
            "lv": "4",
            "regSeCd": "1",
            "type": "json",
        }
        rows = await fetch_all_pages(MOIS_AGE_URL, params)
        return [r for r in rows if str(r.get("stdgCd", "")).startswith(legal_dong_code[:8])]

    async def _upsert_snap_row(self, legal_dong_code: str, raw: dict, stats_ym: str) -> None:
        village = (
            await self._session.execute(select(VillageOrm).where(VillageOrm.emd_code == legal_dong_code))
        ).scalar_one_or_none()
        if not village:
            return

        year = int(stats_ym[:4])
        month = int(stats_ym[4:6])
        snapshot_date = date(year, month, 1)

        existing = (
            await self._session.execute(
                select(SnapPopulationOrm)
                .where(SnapPopulationOrm.village_id == village.id)
                .order_by(desc(SnapPopulationOrm.snapshot_date))
                .limit(1)
            )
        ).scalar_one_or_none()

        if existing:
            for field in (
                "population_total",
                "population_65plus",
                "population_youth",
                "registered_households",
                "net_youth_migration",
            ):
                value = raw.get(field)
                if value is not None:
                    setattr(existing, field, value)
            existing.snapshot_date = snapshot_date
        else:
            self._session.add(
                SnapPopulationOrm(
                    village_id=village.id,
                    snapshot_date=snapshot_date,
                    population_total=raw.get("population_total"),
                    population_65plus=raw.get("population_65plus"),
                    population_youth=raw.get("population_youth"),
                    registered_households=raw.get("registered_households"),
                )
            )
        await self._session.flush()
