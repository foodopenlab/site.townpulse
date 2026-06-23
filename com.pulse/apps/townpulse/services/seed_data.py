from __future__ import annotations

import uuid
from datetime import date, datetime

# 충북 10개 시·군 + TAGO city codes (probe SSOT)
SIGUNGU_SEED = [
    {"sigungu": "청주시", "sigungu_code": "43111", "tago_city_code": "33010"},
    {"sigungu": "충주시", "sigungu_code": "43130", "tago_city_code": "33020"},
    {"sigungu": "제천시", "sigungu_code": "43150", "tago_city_code": "33030"},
    {"sigungu": "보은군", "sigungu_code": "43720", "tago_city_code": "33040"},
    {"sigungu": "옥천군", "sigungu_code": "43730", "tago_city_code": "33050"},
    {"sigungu": "영동군", "sigungu_code": "43740", "tago_city_code": "33060"},
    {"sigungu": "증평군", "sigungu_code": "43745", "tago_city_code": None},
    {"sigungu": "진천군", "sigungu_code": "43750", "tago_city_code": "33080"},
    {"sigungu": "괴산군", "sigungu_code": "43760", "tago_city_code": "33090"},
    {"sigungu": "음성군", "sigungu_code": "43770", "tago_city_code": "33100"},
    {"sigungu": "단양군", "sigungu_code": "43800", "tago_city_code": "33110"},
]

# 데모 마을 고정
DEMO_VILLAGE_CODE = "4300025000"
DEMO_VILLAGE_NAME = "영춘면"
DEMO_LAT = 36.637
DEMO_LNG = 127.489

# MVP 제출용 QA 로그인 (프론트·백엔드 SSOT)
MVP_QA_ORG_UUID = uuid.UUID("00000000-0000-4000-8000-000000000001")
MVP_QA_LOGIN_ID = "1234"
MVP_QA_PASSWORD = "1234"

from apps.townpulse.services.chungbuk_village_names import village_name_for

PRESCRIPTION_TYPES = [
    {"code": "VACANT_BUYBACK", "name": "빈집 매입·리모델링", "category": "housing", "rollout_timeline": "urgent"},
    {"code": "DRT", "name": "수요응답형 버스(DRT)", "category": "transport", "rollout_timeline": "medium"},
    {"code": "INCENTIVE", "name": "청년 정착 인센티브", "category": "population", "rollout_timeline": "medium"},
    {"code": "SOC_COMPLEX", "name": "주민복합커뮤니티센터", "category": "welfare", "rollout_timeline": "long"},
    {"code": "ELDERLY_CARE", "name": "돌봄·경로당 확충", "category": "welfare", "rollout_timeline": "medium"},
]

DISPATCH_RULES = [
    {"code": "VACANT_BUYBACK", "trigger": "vacancy_rate", "operator": "gte", "threshold": 0.15, "rank": 1},
    {"code": "DRT", "trigger": "bus_interval_score", "operator": "lte", "threshold": 0.3, "rank": 2},
    {"code": "INCENTIVE", "trigger": "pop_decline_score", "operator": "gte", "threshold": 0.5, "rank": 3},
]

BUDGET_PRICES = [
    {"code": "VACANT_BUYBACK", "unit": "호", "min": 15000, "max": 45000},
    {"code": "DRT", "unit": "대", "min": 8000, "max": 20000},
    {"code": "INCENTIVE", "unit": "가구", "min": 500, "max": 3000},
    {"code": "SOC_COMPLEX", "unit": "건", "min": 50000, "max": 120000},
    {"code": "ELDERLY_CARE", "unit": "시설", "min": 10000, "max": 35000},
]

PRESCRIPTION_INDICATORS = [
    {"code": "VACANT_BUYBACK", "indicator_code": "vacancy_rate", "effect_direction": "decrease"},
    {"code": "DRT", "indicator_code": "bus_interval_score", "effect_direction": "increase"},
    {"code": "INCENTIVE", "indicator_code": "pop_decline_score", "effect_direction": "decrease"},
    {"code": "SOC_COMPLEX", "indicator_code": "vacancy_rate", "effect_direction": "decrease"},
    {"code": "ELDERLY_CARE", "indicator_code": "aging_ratio", "effect_direction": "decrease"},
]

# 시군구 대표 좌표 (MVP 지도용 — vworld 미동기화 시 분산 배치)
SIGUNGU_CENTERS: dict[str, tuple[float, float]] = {
    "청주시": (36.642, 127.489),
    "충주시": (36.991, 127.926),
    "제천시": (37.132, 128.191),
    "보은군": (36.489, 127.729),
    "옥천군": (36.306, 127.571),
    "영동군": (36.175, 127.776),
    "증평군": (36.785, 127.581),
    "진천군": (36.855, 127.443),
    "괴산군": (36.815, 127.786),
    "음성군": (36.940, 127.690),
    "단양군": (36.984, 128.365),
}


def village_coords_for(sigungu: str, index_in_sigungu: int) -> tuple[float, float]:
    """시군구 중심 주변 격자 오프셋 — 대각선 일렬 배치 방지."""
    base_lat, base_lng = SIGUNGU_CENTERS.get(sigungu, (36.6, 127.5))
    row, col = divmod(index_in_sigungu, 5)
    lat = base_lat + (row - 2) * 0.028 + (index_in_sigungu % 3) * 0.006
    lng = base_lng + (col - 2) * 0.032 + (index_in_sigungu % 4) * 0.005
    return round(lat, 6), round(lng, 6)


def generate_village_rows(total: int = 228) -> list[dict]:
    rows: list[dict] = []
    per_sigungu = total // len(SIGUNGU_SEED)
    remainder = total % len(SIGUNGU_SEED)
    seq = 1
    for idx, sig in enumerate(SIGUNGU_SEED):
        count = per_sigungu + (1 if idx < remainder else 0)
        for i in range(count):
            if sig["sigungu"] == "단양군" and i == 0:
                emd_code = DEMO_VILLAGE_CODE
                name = DEMO_VILLAGE_NAME
            else:
                emd_code = f"43{sig['sigungu_code'][2:]}{seq:05d}"[:10].ljust(10, "0")
                if len(emd_code) > 10:
                    emd_code = emd_code[:10]
                name_idx = i - 1 if sig["sigungu"] == "단양군" else i
                name = village_name_for(sig["sigungu"], name_idx)
            lat, lng = (
                (DEMO_LAT, DEMO_LNG)
                if emd_code == DEMO_VILLAGE_CODE
                else village_coords_for(sig["sigungu"], i)
            )
            rows.append(
                {
                    "emd_code": emd_code,
                    "name": name,
                    "sigungu": sig["sigungu"],
                    "sigungu_code": sig["sigungu_code"],
                    "tago_city_code": sig["tago_city_code"],
                    "legal_dong_code": emd_code,
                    "lat": lat,
                    "lng": lng,
                }
            )
            seq += 1
    return rows[:total]
