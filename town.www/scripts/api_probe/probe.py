"""
TownPulse 공공API 필드 검증 프로브.

사용법:
  cd town.www/scripts/api_probe
  pip install -r requirements.txt
  # API 키는 town.www/.env.local (probe.py가 자동 로드)
  # endpoints.yaml 에 Swagger URL·params 입력 후 enabled: true
  python probe.py
  python probe.py --id 15108071_household
  python probe.py --list-keys   # 응답 첫 item의 JSON 키만 출력
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import httpx
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT / ".env.local"
SAMPLES_DIR = ROOT / "_docs" / "api_samples"
CONFIG_PATH = Path(__file__).resolve().parent / "endpoints.yaml"

ENV_PATTERN = re.compile(r"\$\{([A-Z0-9_]+)\}")


def resolve_value(raw: Any, env: dict[str, str]) -> Any:
    if isinstance(raw, str):
        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            val = env.get(key, "")
            if not val:
                raise KeyError(f"환경 변수 {key} 가 .env.local 에 없습니다.")
            return val

        return ENV_PATTERN.sub(repl, raw)
    if isinstance(raw, dict):
        return {k: resolve_value(v, env) for k, v in raw.items()}
    if isinstance(raw, list):
        return [resolve_value(v, env) for v in raw]
    return raw


def find_first_item(obj: Any) -> dict[str, Any] | None:
    if isinstance(obj, dict):
        if "item" in obj:
            item = obj["item"]
            if isinstance(item, list) and item:
                first = item[0]
                return first if isinstance(first, dict) else None
            if isinstance(item, dict):
                return item
        for value in obj.values():
            found = find_first_item(value)
            if found:
                return found
    elif isinstance(obj, list):
        for value in obj:
            found = find_first_item(value)
            if found:
                return found
    return None


def load_probes() -> list[dict[str, Any]]:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("probes", [])


def run_probe(probe: dict[str, Any], env: dict[str, str], list_keys: bool) -> int:
    probe_id = probe["id"]
    if not probe.get("enabled"):
        print(f"[SKIP] {probe_id} - enabled: false (endpoints.yaml 에 URL 입력 후 true)")
        return 0

    url = (probe.get("url") or "").strip()
    if not url:
        print(f"[SKIP] {probe_id} - url 비어 있음")
        return 1

    params = resolve_value(probe.get("params") or {}, env)
    timeout = float(probe.get("timeout_sec") or 30)

    name = str(probe.get("name", probe_id)).encode("ascii", "replace").decode()
    print(f"[CALL] {name}")
    print(f"       {url}")

    with httpx.Client(timeout=timeout) as client:
        response = client.get(url, params=params)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "json" in content_type or response.text.lstrip().startswith("{"):
        payload: Any = response.json()
    else:
        payload = {"_raw_xml": response.text[:5000]}

    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SAMPLES_DIR / f"{probe_id}.json"
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[SAVE] {out_path.relative_to(ROOT)}")

    item = find_first_item(payload)
    if list_keys and item:
        keys = sorted(item.keys())
        print(f"[KEYS] {len(keys)} fields: {', '.join(keys[:20])}")
        if len(keys) > 20:
            print(f"       ... +{len(keys) - 20} more")
    elif list_keys:
        print("[KEYS] item 노드를 찾지 못했습니다 — 저장된 JSON 직접 확인")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="TownPulse API field probe")
    parser.add_argument("--id", help="특정 probe id 만 실행")
    parser.add_argument("--list-keys", action="store_true", help="응답 item 키 목록 출력")
    args = parser.parse_args()

    if not ENV_PATH.exists():
        print(f".env.local 없음: {ENV_PATH}")
        print("  town.www/.env.local 에 API 키·PROBE_* 좌표를 입력하세요.")
        return 1

    load_dotenv(ENV_PATH)
    env = dict(os.environ)
    probes = load_probes()

    if args.id:
        probes = [p for p in probes if p.get("id") == args.id]
        if not probes:
            print(f"probe id '{args.id}' 를 찾을 수 없습니다.")
            return 1

    errors = 0
    for probe in probes:
        try:
            errors += run_probe(probe, env, args.list_keys)
        except httpx.HTTPStatusError as exc:
            print(f"[HTTP {exc.response.status_code}] {probe.get('id')}: {exc.response.text[:300]}")
            errors += 1
        except Exception as exc:
            print(f"[ERROR] {probe.get('id')}: {exc}")
            errors += 1

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
