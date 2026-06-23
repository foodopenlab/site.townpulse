#!/usr/bin/env python3
"""228 읍면동 중심 좌표 기반 GeoJSON 생성 (실제 행정구역 경계 매핑 및 합성 폴리곤 폴백)."""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apps.townpulse.services.seed_data import generate_village_rows

OUT = ROOT.parent / "town.www" / "public" / "geojson" / "chungbuk_emd.geojson"
DELTA = 0.014
GITHUB_GEOJSON_URL = "https://raw.githubusercontent.com/raqoon886/Local_HangJeongDong/master/hangjeongdong_%E1%85%AE%E1%86%BC%E1%84%8E%E1%85%A5%E1%86%BC%E1%84%87%E1%85%AE%E1%86%A8%E1%84%83%E1%85%A9.geojson"


async def get_villages_from_db() -> list[dict]:
    """DB에서 실제 저장된 마을 데이터(실제 emd_code 등)를 조회합니다."""
    try:
        from core.matrix.grid_keymaker_secret_manager import get_keymaker
        get_keymaker().load_env()
        from core.matrix.grid_oracle_database_manager import get_session_factory
        from apps.townpulse.adapter.outbound.orm.models import VillageOrm, RegionOrm
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        factory = get_session_factory()
        async with factory() as session:
            stmt = select(VillageOrm).options(selectinload(VillageOrm.region))
            rows = (await session.execute(stmt)).scalars().all()
            return [
                {
                    "emd_code": v.emd_code,
                    "name": v.name,
                    "sigungu": v.region.sigungu if v.region else None,
                    "lat": v.lat,
                    "lng": v.lng
                }
                for v in rows
            ]
    except Exception as e:
        print(f"DB 조회 실패 ({e}), 시드 데이터로 폴백합니다.", flush=True)
        return []


def download_real_geojson() -> dict | None:
    """GitHub contents API를 통해 충청북도 GeoJSON 파일을 동적으로 찾아 다운로드합니다."""
    try:
        print("Discovering GeoJSON URL from GitHub API...", flush=True)
        list_url = "https://api.github.com/repos/raqoon886/Local_HangJeongDong/contents"
        req = urllib.request.Request(list_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            files = json.loads(resp.read().decode('utf-8'))
            for f in files:
                name = f.get("name", "")
                if "충청북도" in name or "û" in name:
                    download_url = f.get("download_url")
                    if download_url:
                        parts = urllib.parse.urlparse(download_url)
                        path_quoted = urllib.parse.quote(parts.path)
                        url_quoted = urllib.parse.urlunparse((parts.scheme, parts.netloc, path_quoted, parts.params, parts.query, parts.fragment))
                        print(f"Downloading from quoted URL: {url_quoted}", flush=True)
                        dreq = urllib.request.Request(url_quoted, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(dreq, timeout=30) as dresp:
                            return json.loads(dresp.read().decode('utf-8'))
        print("Chungbuk GeoJSON file not found in repository.", flush=True)
        return None
    except Exception as e:
        print(f"실제 GeoJSON 다운로드 실패: {e}", flush=True)
        return None


def generate_synthetic_polygon(lat: float, lng: float) -> dict:
    """합성 폴리곤(정사각형)을 생성합니다."""
    ring = [
        [lng - DELTA, lat - DELTA],
        [lng + DELTA, lat - DELTA],
        [lng + DELTA, lat + DELTA],
        [lng - DELTA, lat + DELTA],
        [lng - DELTA, lat - DELTA],
    ]
    return {"type": "Polygon", "coordinates": [ring]}


def main() -> None:
    # 1. DB 또는 Seed에서 마을 목록 조회
    try:
        villages = asyncio.run(get_villages_from_db())
    except Exception:
        villages = []

    if not villages:
        print("Seed 데이터를 사용하여 GeoJSON을 생성합니다.", flush=True)
        villages = [
            {
                "emd_code": row["emd_code"],
                "name": row["name"],
                "sigungu": row["sigungu"],
                "lat": row["lat"],
                "lng": row["lng"]
            }
            for row in generate_village_rows(228)
        ]

    # 2. 실제 GeoJSON 다운로드
    real_geojson = download_real_geojson()
    real_features = real_geojson.get("features", []) if real_geojson else []

    # 3. 매핑 수행
    features = []
    real_match_count = 0
    synthetic_count = 0

    # 빠른 조회를 위해 adm_cd2 prefix로 인덱싱
    # adm_cd2[:8] -> feature
    feature_by_prefix = {}
    for feat in real_features:
        props = feat.get("properties", {})
        adm_cd2 = props.get("adm_cd2")
        if adm_cd2 and len(adm_cd2) >= 8:
            prefix = adm_cd2[:8]
            feature_by_prefix[prefix] = feat

    for v in villages:
        emd_code = v["emd_code"]
        lat, lng = v["lat"], v["lng"]
        
        geometry = None
        # emd_code가 존재하고 실제 10자리 코드인 경우 매핑 시도
        if emd_code and len(emd_code) == 10:
            prefix = emd_code[:8]
            matched_feat = feature_by_prefix.get(prefix)
            if matched_feat:
                geometry = matched_feat.get("geometry")
                real_match_count += 1

        if not geometry:
            if lat is not None and lng is not None:
                geometry = generate_synthetic_polygon(lat, lng)
                synthetic_count += 1
            else:
                continue

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "emd_code": emd_code,
                    "name": v["name"],
                    "sigungu": v["sigungu"]
                },
                "geometry": geometry,
            }
        )

    collection = {"type": "FeatureCollection", "features": features}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT} ({len(features)} features)")
    print(f"  Real EMD boundary matches: {real_match_count}")
    print(f"  Synthetic polygon fallbacks: {synthetic_count}")


if __name__ == "__main__":
    main()
