"""공공데이터포털 OpenAPI HTTP 클라이언트 — Keymaker 외부, httpx 단일 진입점."""
from __future__ import annotations

from typing import Any
import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)

MOIS_HOUSEHOLD_URL = (
    "https://apis.data.go.kr/1741000/stdgPpltnHhStus/selectStdgPpltnHhStus"
)
MOIS_AGE_URL = "https://apis.data.go.kr/1741000/stdgSexdAgePpltn/selectStdgSexdAgePpltn"
MOIS_MIGRATION_URL = "https://apis.data.go.kr/1741000/ppltnDataStus/selectPpltnDataStus"
BUILDING_HUB_TITLE_URL = "https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo"
BUS_ROUTE_LIST_URL = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList"
BUS_ROUTE_INFO_URL = "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem"
BUS_ROUTE_STOPS_URL = (
    "https://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList"
)
BUS_STOP_NEARBY_URL = "https://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList"
VWORLD_ADDRESS_URL = "https://api.vworld.kr/req/address"
FISCAL_SELF_RLT_URL = (
    "https://apis.data.go.kr/1741000/localFinanceSelfRltRateList/getLocalFinanceSelfRltRateList"
)


def extract_response_items(body: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(body, dict):
        return []
    if "Response" in body:
        resp = body.get("Response")
        if not isinstance(resp, dict):
            return []
        items_container = resp.get("items")
        if not isinstance(items_container, dict):
            return []
        items = items_container.get("item")
    elif "response" in body:
        resp = body.get("response")
        if not isinstance(resp, dict):
            return []
        resp_body = resp.get("body")
        if not isinstance(resp_body, dict):
            return []
        items_container = resp_body.get("items")
        if not isinstance(items_container, dict):
            return []
        items = items_container.get("item")
    else:
        return []
    if items is None or items == "":
        return []
    if isinstance(items, dict):
        return [items]
    return list(items)


def extract_total_count(body: dict[str, Any]) -> int:
    if not isinstance(body, dict):
        return 0
    if "Response" in body:
        resp = body.get("Response")
        if not isinstance(resp, dict):
            return 0
        head = resp.get("head")
        if not isinstance(head, dict):
            return 0
        raw = head.get("totalCount", 0)
    elif "response" in body:
        resp = body.get("response")
        if not isinstance(resp, dict):
            return 0
        resp_body = resp.get("body")
        if not isinstance(resp_body, dict):
            return 0
        raw = resp_body.get("totalCount", 0)
    else:
        return 0
    try:
        return int(raw or 0)
    except (TypeError, ValueError):
        return 0


def mois_result_ok(body: dict[str, Any]) -> bool:
    if not isinstance(body, dict):
        return False
    resp = body.get("Response")
    if not isinstance(resp, dict):
        return False
    head = resp.get("head")
    if not isinstance(head, dict):
        return False
    code = str(head.get("resultCode", ""))
    return code in ("0", "00", "000")


def building_result_ok(body: dict[str, Any]) -> bool:
    if not isinstance(body, dict):
        return False
    resp = body.get("response")
    if not isinstance(resp, dict):
        return False
    header = resp.get("header")
    if not isinstance(header, dict):
        return False
    code = str(header.get("resultCode", ""))
    return code in ("0", "00", "000")


async def fetch_json(
    url: str,
    params: dict[str, Any],
    *,
    timeout: float = 30.0,
) -> dict[str, Any]:
    max_retries = 3
    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            if attempt == max_retries:
                logger.error(f"Failed to fetch from {url} after {max_retries} retries: {exc}")
                raise
            
            backoff_sec = 2 ** attempt
            logger.warning(
                f"Fetch failed from {url} (attempt {attempt + 1}/{max_retries + 1}): {exc}. "
                f"Retrying in {backoff_sec}s..."
            )
            await asyncio.sleep(backoff_sec)
    raise RuntimeError(f"Failed to fetch from {url} (unreachable code path)")


async def fetch_all_pages(
    url: str,
    base_params: dict[str, Any],
    *,
    page_param: str = "pageNo",
    rows_param: str = "numOfRows",
    page_size: int = 1000,
) -> list[dict[str, Any]]:
    all_items: list[dict[str, Any]] = []
    page = 1
    while True:
        params = {**base_params, page_param: page, rows_param: page_size}
        body = await fetch_json(url, params)
        batch = extract_response_items(body)
        if not batch:
            break
        all_items.extend(batch)
        total = extract_total_count(body)
        if total <= 0 or page * page_size >= total:
            break
        page += 1
    return all_items


def extract_single_item(body: dict[str, Any]) -> dict[str, Any] | None:
    items = extract_response_items(body)
    return items[0] if items else None
