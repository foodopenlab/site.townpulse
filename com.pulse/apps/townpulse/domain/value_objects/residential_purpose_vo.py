"""건축법 시행령 별표1 기준 주거용도 화이트리스트 — §10-8b."""
from __future__ import annotations

RESIDENTIAL_PURPOSE_NAMES: frozenset[str] = frozenset({
    "단독주택",
    "다중주택",
    "다가구주택",
    "공동주택",
    "아파트",
    "연립주택",
    "다세대주택",
})


def is_residential(main_purps_nm: str | None) -> bool:
    if not main_purps_nm:
        return False
    return main_purps_nm.strip() in RESIDENTIAL_PURPOSE_NAMES
