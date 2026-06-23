#!/usr/bin/env python3
"""MVP 로컬 QA 스모크 테스트."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from apps.townpulse.adapter.inbound.api import ROUTERS  # noqa: E402
from main import app  # noqa: E402


def main() -> int:
    failures = 0
    with TestClient(app) as client:
        openapi = client.get("/openapi.json").json()
        paths = [p for p in openapi["paths"] if p.startswith("/api/townpulse/")]
        print(f"routers registered: {len(ROUTERS)}")
        print(f"openapi townpulse paths: {len(paths)}")

        demo = client.post("/api/townpulse/users/demo/token").json()
        demo_headers = {"Authorization": f"Bearer {demo['access_token']}"}

        report_post = client.post(
            "/api/townpulse/reports",
            headers=demo_headers,
            json={"village_id": "00000000-0000-0000-0000-000000000001", "title": "t"},
        )
        report_data = client.post(
            "/api/townpulse/report-data/4300025000",
            headers=demo_headers,
            json={"format": "pdf"},
        )
        print(f"demo reports POST: {report_post.status_code} (expect 403)")
        print(f"demo report-data POST: {report_data.status_code} (expect 403)")

        if len(ROUTERS) != 22:
            failures += 1
        if report_post.status_code != 403:
            failures += 1
        if report_data.status_code != 403:
            failures += 1

    print("PASS" if failures == 0 else f"FAIL ({failures} checks)")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
