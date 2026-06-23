#!/usr/bin/env python3
"""공공API·필수 환경 변수 검증."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.matrix.grid_keymaker_secret_manager import get_keymaker

REQUIRED = ("DATABASE_URL", "JWT_SECRET")
API_KEYS = (
    "POPULATION_HOUSEHOLD_API_KEY",
    "POPULATION_AGE_API_KEY",
    "POPULATION_MIGRATION_API_KEY",
    "BUILDING_HUB_API_KEY",
    "VWORLD_API_KEY",
    "BUS_ROUTE_API_KEY",
    "FISCAL_RELIANCE_API_KEY",
    "GEMINI_API_KEY",
)
OPTIONAL = ("BUS_STOP_API_KEY", "GEMINI_MODEL", "KOSIS_API_KEY")


def main() -> int:
    km = get_keymaker()
    km.load_env()
    missing: list[str] = []
    for key in REQUIRED:
        if not km.get_secret(key):
            missing.append(key)
    if missing:
        print("필수 키 누락:", ", ".join(missing))
        return 1

    print("필수 키 OK")
    for key in API_KEYS:
        status = "OK" if km.get_secret(key) else "MISSING"
        print(f"  {key}: {status}")
    for key in OPTIONAL:
        if km.get_secret(key):
            print(f"  {key}: OK (optional)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
