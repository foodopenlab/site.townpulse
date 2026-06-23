#!/usr/bin/env python3
"""전체 공공데이터 sync — Phase A → B(0~2) → C → fiscal."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core.matrix.grid_keymaker_secret_manager import get_keymaker

BASE = os.getenv("TOWNPULSE_API_BASE", "http://127.0.0.1:8000/api/townpulse")
PHASE_A_TIMEOUT_SEC = int(os.getenv("SYNC_PHASE_A_TIMEOUT_SEC", str(8 * 3600)))  # 기본 8시간


def _request(method: str, path: str, token: str | None, body: dict | None = None) -> dict:
    url = f"{BASE}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=600) as resp:
        raw = resp.read().decode()
        return json.loads(raw) if raw else {}


def _login() -> str:
    org_id = os.getenv("SYNC_ORG_ID", "1234")
    password = os.getenv("SYNC_PASSWORD", "1234")
    payload = _request("POST", "/users/login", None, {"org_id": org_id, "password": password})
    return payload["access_token"]


def _parse_started_at(value: str | None) -> float | None:
    if not value:
        return None
    try:
        if not value.endswith("Z") and "+" not in value and "-" not in value[10:]:
            value = value + "Z"
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        return None


def _get_latest_job(token: str) -> dict | None:
    try:
        return _request("GET", "/admin/sync/jobs/latest", token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def _poll_latest(token: str, label: str, timeout_sec: int | None = None, *, not_before: float | None = None) -> None:
    if timeout_sec is None:
        timeout_sec = PHASE_A_TIMEOUT_SEC
    deadline = time.time() + timeout_sec
    last_status = None
    while time.time() < deadline:
        try:
            job = _request("GET", "/admin/sync/jobs/latest", token)
        except urllib.error.HTTPError:
            time.sleep(10)
            continue
        started = _parse_started_at(job.get("started_at"))
        if not_before is not None and started is not None and started < not_before:
            time.sleep(5)
            continue
        status = job.get("status")
        if status != last_status:
            print(f"  [{label}] status={status} processed={job.get('processed_count')}", flush=True)
            last_status = status
        if status == "COMPLETED":
            return
        if status == "FAILED":
            if not_before is None or (started is not None and started >= not_before):
                raise RuntimeError(job.get("error_message") or "sync failed")
            time.sleep(5)
            continue
        time.sleep(15)
    raise TimeoutError(f"{label} timeout")


def main() -> int:
    get_keymaker().load_env()
    try:
        token = _login()
    except urllib.error.HTTPError as exc:
        print("로그인 실패:", exc.read().decode())
        return 1

    print("Phase A - Chunked Synchronization", flush=True)
 
    # A-0: Resolve legal dong codes first (dong mapping only)
    print("  Step A-0: Resolving legal dong codes...", flush=True)
    trigger_at = time.time()
    _request(
        "POST",
        "/admin/sync/trigger-core?offset=0&limit=1&sync_dong_code=true&sync_core=false&sync_transport=false&sync_tvi=false",
        token,
    )
    _poll_latest(token, "phase-a-0", not_before=trigger_at - 1)
 
    # A-1: Sync core data in chunks of 30 villages
    print("  Step A-1: Syncing core data (population, building, statistics) in chunks...", flush=True)
    chunk_size = 30
    total_villages = 228
    for offset in range(0, total_villages, chunk_size):
        print(f"    Syncing core chunk: offset={offset}, limit={chunk_size}...", flush=True)
        trigger_at = time.time()
        _request(
            "POST",
            f"/admin/sync/trigger-core?offset={offset}&limit={chunk_size}&sync_dong_code=false&sync_core=true&sync_transport=false&sync_tvi=false",
            token,
        )
        _poll_latest(token, f"phase-a-1-core-{offset}", not_before=trigger_at - 1)
 
    # A-2: Sync transport data sigungu by sigungu
    print("  Step A-2: Syncing transport data sigungu by sigungu...", flush=True)
    sigungu_codes = [
        "43111", "43130", "43150", "43720", "43730",
        "43740", "43745", "43750", "43760", "43770", "43800"
    ]
    for sgg in sigungu_codes:
        print(f"    Syncing transport for sigungu={sgg}...", flush=True)
        trigger_at = time.time()
        _request(
            "POST",
            f"/admin/sync/trigger-core?offset=0&limit=228&sync_dong_code=false&sync_core=false&sync_transport=true&sync_tvi=false&sigungu_code={sgg}",
            token,
        )
        _poll_latest(token, f"phase-a-2-transport-{sgg}", not_before=trigger_at - 1)

    for chunk in range(10):
        print(f"Phase B - migration chunk {chunk}", flush=True)
        result = _request("POST", f"/admin/sync/migration-chunk/{chunk}", token)
        print(f"  processed={result.get('processed')} mock={result.get('mock')}", flush=True)

    print("Phase C - finalize TVI", flush=True)
    result = _request("POST", "/admin/sync/finalize", token)
    print(f"  tvi_recalculated={result.get('tvi_recalculated')}", flush=True)

    print("Fiscal - trigger-fiscal", flush=True)
    try:
        result = _request("POST", "/admin/sync/trigger-fiscal", token)
        print(f"  status={result.get('status')}", flush=True)
    except urllib.error.HTTPError as exc:
        print("  fiscal skip:", exc.read().decode()[:200], flush=True)

    print("Done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
