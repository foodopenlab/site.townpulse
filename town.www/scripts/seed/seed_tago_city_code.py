"""
town.www/_docs/api_samples/tago_city_codes_chungbuk.json (getCtyCodeList 충북 probe 결과)을
REGION.tago_city_code 컬럼에 매핑하는 1회성 시드 스크립트.

전제:
  - probe.py --id tago_city_codes 실행 후 tago_city_codes_chungbuk.json 생성됨
  - REGION 기본 행(시·군명)은 별도 시드 완료 상태

사용 (구현 후):
  cd town.www
  python -m scripts.seed.seed_tago_city_code
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_PATH = ROOT / "_docs" / "api_samples" / "tago_city_codes_chungbuk.json"


def load_probe_result() -> list[dict]:
    if not SAMPLE_PATH.exists():
        raise FileNotFoundError(
            f"{SAMPLE_PATH} 없음 — probe.py --id tago_city_codes 실행 후 "
            "tago_city_codes_chungbuk.json 확인"
        )
    data = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
    return data["items"]


async def seed(session) -> dict:
    """REGION.sigungu_name ↔ TAGO cityname 매칭 후 tago_city_code UPDATE."""
    items = load_probe_result()
    updated: list[tuple[str, str]] = []
    unmatched: list[tuple[str, str]] = []

    for item in items:
        raw_name = str(item["cityname"]).strip()
        city_code = str(item["citycode"]).strip()
        result = await session.execute(
            "UPDATE region SET tago_city_code = :code WHERE sigungu_name = :name",
            {"code": city_code, "name": raw_name},
        )
        if result.rowcount:
            updated.append((raw_name, city_code))
        else:
            unmatched.append((raw_name, city_code))

    await session.commit()
    return {"updated": len(updated), "updated_pairs": updated, "unmatched": unmatched}
