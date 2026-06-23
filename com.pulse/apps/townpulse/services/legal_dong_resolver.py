"""행안부 API lv=3으로 읍·면·동 법정동코드를 조회해 village.emd_code에 매핑."""
from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.townpulse.adapter.outbound.orm.models import VillageOrm
from core.matrix.grid_public_api_client import (
    MOIS_HOUSEHOLD_URL,
    fetch_all_pages,
)

logger = logging.getLogger(__name__)


def current_stats_ym(months_ago: int = 3) -> str:
    today = date.today()
    month = today.month - months_ago
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    return f"{year}{month:02d}"


def _normalize_name(name: str) -> str:
    return name.strip().replace(" ", "")


def _dong_label(row: dict) -> str:
    li = row.get("liNm")
    if li and str(li).strip():
        return _normalize_name(str(li))
    for key in ("dongNm", "stdgNm"):
        value = row.get(key)
        if value and str(value).strip():
            return _normalize_name(str(value))
    return ""


def _candidate_rows(dongs: list[dict], village_name: str) -> list[dict]:
    """읍·면·동은 stdgCd 끝 2자리 00, 리 명칭은 00이 아닌 코드 우선."""
    is_ri = _normalize_name(village_name).endswith("리")
    result: list[dict] = []
    for row in dongs:
        code = str(row.get("stdgCd") or "").strip()
        if len(code) != 10:
            continue
        if is_ri:
            if code[8:10] != "00":
                result.append(row)
        elif code[8:10] == "00":
            result.append(row)
    return result or dongs


def _names_compatible(village_name: str, api_name: str) -> bool:
    village = _normalize_name(village_name)
    api = _normalize_name(api_name)
    if not village or not api:
        return False
    if village == api:
        return True

    # 읍/면과 리/동 간의 잘못된 매칭 방지 (서로 다른 행정구역 레벨)
    village_is_township = village.endswith(("읍", "면"))
    api_is_township = api.endswith(("읍", "면"))
    village_is_village = village.endswith(("리", "동"))
    api_is_village = api.endswith(("리", "동"))

    if (village_is_township and api_is_village) or (village_is_village and api_is_township):
        return False

    for suffix in ("리", "면", "읍", "동"):
        if village.endswith(suffix) and village[:-1] == api:
            return True
        if api.endswith(suffix) and api[:-1] == village:
            return True
        # 단일 글자(예: "상")의 부분 일치로 인한 오매칭 방지를 위해 길이 제한(2글자 이상) 추가
        if village.endswith(suffix) and len(village[:-1]) >= 2 and village[:-1] in api:
            return True
        if api.endswith(suffix) and len(api[:-1]) >= 2 and api[:-1] in village:
            return True
    return (len(village) >= 2 and village in api) or (len(api) >= 2 and api in village)



async def discover_dongs_for_sigungu(
    sigungu_code: str,
    stats_ym: str,
    api_key: str,
) -> list[dict]:
    params = {
        "serviceKey": api_key,
        "stdgCd": f"{sigungu_code}00000",
        "srchFrYm": stats_ym,
        "srchToYm": stats_ym,
        "lv": "3",
        "regSeCd": "1",
        "type": "json",
    }
    rows = await fetch_all_pages(MOIS_HOUSEHOLD_URL, params)
    by_code: dict[str, dict] = {}
    for row in rows:
        code = str(row.get("stdgCd") or "").strip()
        if len(code) == 10 and code not in by_code:
            by_code[code] = row
    return list(by_code.values())


async def resolve_village_legal_dong_codes(session: AsyncSession, household_api_key: str) -> int:
    if not household_api_key:
        return 0

    stats_ym = current_stats_ym()
    villages = (
        await session.execute(select(VillageOrm).options(selectinload(VillageOrm.region)))
    ).scalars().all()

    by_sigungu: dict[str, list[VillageOrm]] = defaultdict(list)
    for village in villages:
        if village.region and village.region.sigungu_code:
            by_sigungu[village.region.sigungu_code].append(village)

    updated = 0
    for sigungu_code, group in by_sigungu.items():
        try:
            dongs = await discover_dongs_for_sigungu(sigungu_code, stats_ym, household_api_key)
        except Exception as exc:
            logger.warning("legal_dong_discovery_failed sigungu=%s err=%s", sigungu_code, exc)
            continue
        if not dongs:
            continue

        used_codes: set[str] = set()
        for village in group:
            matched_code: str | None = None
            candidates = _candidate_rows(dongs, village.name)
            for row in candidates:
                code = str(row.get("stdgCd") or "").strip()
                if not code or code in used_codes:
                    continue
                label = _dong_label(row)
                if label and _names_compatible(village.name, label):
                    matched_code = code
                    break
            if matched_code and matched_code != village.emd_code:
                village.emd_code = matched_code
                used_codes.add(matched_code)
                updated += 1
            elif matched_code:
                used_codes.add(matched_code)

    if updated:
        await session.flush()
    return updated
