"""
TVI finalize 직후 1회 실행 — 충북 228개 마을 PRESCRIPTION_RESULT 사전 생성 (§12-1d OPTIONAL).

- POST /prescription-results = dispatch_rule + DB insert (Gemini 없음)
- ai_description은 None — 클릭 시 GET .../stream 에서 실시간 생성
- 멱등: by-village 에 row 있으면 skip
- 선행: seed_qa_account.py (§12-1c), recalculate_all() 완료

사용:
  cd town.www
  API_BASE_URL=https://api.townpulse.site/api/townpulse python -m scripts.seed.seed_all_prescriptions
"""
from __future__ import annotations

import asyncio
import os

import httpx

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000/api/townpulse").rstrip("/")
ADMIN_ORG_ID = os.environ["QA_SEED_ORG_ID"]
ADMIN_PASSWORD = os.environ["QA_SEED_PASSWORD"]


async def main() -> None:
    async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
        login = await client.post(
            "/users/login",
            json={"org_id": ADMIN_ORG_ID, "password": ADMIN_PASSWORD},
        )
        login.raise_for_status()
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        villages_resp = await client.get("/dashboard/map/villages", headers=headers)
        villages_resp.raise_for_status()
        villages = villages_resp.json()["villages"]
        print(f"대상 마을 {len(villages)}곳")

        created, skipped, empty_match, failed = 0, 0, 0, 0

        for v in villages:
            village_id = v.get("village_id")
            village_code = v.get("village_code", "?")
            village_name = v.get("village_name") or v.get("name") or village_code

            if not village_id:
                failed += 1
                print(f"  ⚠ village_id 없음 {village_code} — map/villages 응답 확인")
                continue

            existing = await client.get(
                f"/prescription-results/by-village/{village_id}",
                headers=headers,
            )
            if existing.status_code == 200 and existing.json().get("total", 0) > 0:
                skipped += 1
                continue

            gen = await client.post(
                "/prescription-results",
                json={"village_id": village_id},
                headers=headers,
            )
            if gen.status_code != 200:
                failed += 1
                body = gen.text[:150]
                print(f"  ⚠ 생성 실패 {village_name} → {gen.status_code} {body}")
                continue

            total = gen.json().get("total", 0)
            if total == 0:
                empty_match += 1
            else:
                created += 1

        print(
            f"완료 — 신규 생성 {created} / 매칭 0건(정상) {empty_match} "
            f"/ 이미 존재 {skipped} / 실패 {failed}"
        )


if __name__ == "__main__":
    asyncio.run(main())
