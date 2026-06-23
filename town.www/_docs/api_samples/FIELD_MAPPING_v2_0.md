# API 필드 매핑 — 실호출 결과 (2026-06-21)

> 샘플 JSON: `town.www/_docs/api_samples/`. MOIS 3종 URL·필드 **2026-06-21 probe 확정**.

## ✅ API#2 인구·세대 — `15108071_household.json` (확정 2026-06-21)

**URL:** `https://apis.data.go.kr/1741000/stdgPpltnHhStus/selectStdgPpltnHhStus`

| JSON 키 | SNAP 컬럼 | 한글 | 비고 |
|---|---|---|---|
| `totNmprCnt` | `population_total` | 총인구수 | integer 변환 |
| `hhCnt` | `registered_households` | 세대수 | integer 변환 |
| `stdgCd` | `REGION.legal_dong_code` | 법정동코드 | 조인키 |
| `statsYm` | `snapshot_date` | 통계년월 | YYYYMM → DATE |
| `maleNmprCnt` | (참조) | 남자인구수 | |
| `femlNmprCnt` | (참조) | 여자인구수 | |
| `maleFemlRate` | (참조) | 남녀비율 | |
| `tong`, `ban` | (집계용) | 통·반 | lv=4 → **동일 stdgCd 행 합산** 후 1 SNAP행 |

**resultCode:** `"0"` + `NORMAL_SERVICE` (국토부 API `"00"`과 다름)

**ingest 주의:** `lv=4`면 통·반별 **여러 item** → `stdgCd`+`statsYm` 기준 `totNmprCnt`·`hhCnt` **SUM** 후 upsert.

---

## ✅ API#3 성/연령 — `15108074_age.json` (확정 2026-06-21)

**URL:** `https://apis.data.go.kr/1741000/stdgSexdAgePpltn/selectStdgSexdAgePpltn`  
(URL 대소문자 주의 — `StdgSexdAgePpltn` → HTTP 500)

**params:** #2와 동일 (`stdgCd`, `srchFrYm`, `srchToYm`, `lv=4`, `regSeCd=1`)

| JSON 키 패턴 | SNAP 컬럼 | 비고 |
|---|---|---|
| `male{N}AgeNmprCnt` / `feml{N}AgeNmprCnt` | (집계용) | **10세 구간** — N=0,10,20,…,100 |
| `stdgCd` | `REGION.legal_dong_code` | 조인키 |
| `statsYm` | `snapshot_date` | YYYYMM |
| `totNmprCnt` | (검증용) | #2 `population_total`과 대조 |
| `tong`, `ban` | (집계용) | lv=4 → **stdgCd+statsYm SUM** |

**SNAP 파생 (10세 구간 한계):**

```text
population_65plus  = sum(male70,80,90,100 + feml70,80,90,100 AgeNmprCnt)   # 70세 이상
population_youth   = sum(male20,30 + feml20,30 AgeNmprCnt)                 # 20~39세
```

> 65~69세는 10세 구간(`male60Age`)에 포함되어 **별도 분리 불가**. 정확한 65+가 필요하면 팀에서 60세 구간 포함 여부 합의.

**ingest:** #2와 동일 — 통·반 다건 → `stdgCd`+`statsYm` 합산 후 upsert.

---

## ✅ API#4 인구이동 — `15108093_migration.json` (확정 2026-06-21)

**URL:** `https://apis.data.go.kr/1741000/ppltnDataStus/selectPpltnDataStus`

| Swagger | yaml | 비고 |
|---|---|---|
| mvinAdmmCd * | `PROBE_MVIN_ADMM_CD` | 전입 **행정기관코드** (예: `4311152500`) |
| mvtAdmmCd * | `PROBE_MVT_ADMM_CD` | 전출지 (**필수**) — 전국→전입지: `1100000000`(서울) 등 |
| srchFrYm / srchToYm | `PROBE_SRCH_*` | YYYYMM |
| lv (3) | `"3"` | 읍·면·동 |
| regSeCd | **없음** | |

| JSON 키 | SNAP / 용도 | 비고 |
|---|---|---|
| `male{N}AgeNmprCnt` / `feml{N}AgeNmprCnt` | (집계용) | **만 N세 단일 연령** (0~110+) |
| `mvinAdmmCd` | `net_youth_migration` 집계 | **행정기관코드** — `emd_code`/`admmCd` (≠ `legal_dong_code`) |
| `mvinDongNm`, `mvtCtpvNm` 등 | (참조) | 지명 |
| `statsYm` | `snapshot_date` | |
| `totNmprCnt` | (검증용) | 해당 전입·전출 쌍 합계 |

**SNAP 파생 (SSOT: 백엔드 §10-8-1):**

```text
admm_cd = REGION.emd_code or mode(API#2.admmCd)   # legal_dong_code 직접 사용 금지
youth_ages = range(20, 40)
total_in  = Σ sido: sum_youth(mvin=admm_cd, mvt=sido_admm_cd(sido))
total_out = Σ sido: sum_youth(mvin=sido_admm_cd(sido), mvt=admm_cd)
net_youth_migration = total_in - total_out
```

> 1회 호출 = (전입지, 전출지) 1쌍 · 34회/법정동 · 월 7,752회 → **3일 분할** (`collect_migration_chunk` 0|1|2)

---

## ✅ API#1 건축HUB — `building_hub_title.json` (요청·응답 확정 v5.1)

**요청 (확정):**

| 파라미터 | 필수 | REGION / 비고 |
|---|---|---|
| `sigunguCd` | ✅ | `sigungu_code` (5자리) |
| `bjdongCd` | ✅ | `legal_dong_code[5:10]` |
| `bun`, `ji` | 선택 | 생략 시 법정동 전체 |
| `numOfRows`, `pageNo` | ✅ | `totalCount`까지 순회 |

| JSON 키 | SNAP / 용도 | 비고 |
|---|---|---|
| `sigunguCd` | `REGION.sigungu_code` | 5자리, 예: `43111` |
| `bjdongCd` | `REGION.legal_dong_code` 후 5자리 | 10자리=`43111`+`10100` |
| `mainPurpsCdNm` | `residential_buildings` 집계 | 화이트리스트 COUNT (7종, §10-8b) · 기숙사 제외 · unmatched 로그 |
| `mainPurpsCd` | 참조 | 코드 |
| `hhldCnt` | **미사용** | 건물 단위 세대 — SNAP에 넣지 않음 |

**URL (확정):** `https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo`  
(구 `BldRgstService_v2` 아님)

**화이트리스트 (정확매칭):** 단독주택·다중주택·다가구주택·공동주택·아파트·연립주택·다세대주택 — 제외: 공관·**기숙사**·오피스텔 (백엔드 §10-8b-1)

---

## ✅ API#6 버스노선 — `bus_route_primary.json` · `bus_route_detail.json` (확정 2026-06-21)

**서비스:** `BusRouteInfoInqireService` (TAGO). data.go.kr **버스노선·TAGO 버스노선정보 = 동일 URL** (probe 동일 응답 → API#7 통합).

**URL:** `https://apis.data.go.kr/1613000/BusRouteInfoInqireService/`

| 호출 | operation | SNAP |
|---|---|---|
| 1단계 | `getRouteNoList` | `bus_route_count`, `routeid` 목록 |
| 2단계 | `getRouteInfoIem` | `avg_bus_interval_min` ← `intervaltime` |

**cityCode:** `REGION.tago_city_code` / `PROBE_BUS_CITY_CODE` — **TAGO 도시코드** (청주 `33010`).  
`sigungu_code`(43111)를 cityCode로 쓰면 **0건**.

**충북 cityCode (getCtyCodeList, probe 2026-06-21):**

| `cityname` | `citycode` |
|---|---|
| 청주시 | `33010` |
| 충주시 | `33020` |
| 제천시 | `33030` |
| 보은군 | `33320` |
| 옥천군 | `33330` |
| 영동군 | `33340` |
| 진천군 | `33350` |
| 괴산군 | `33360` |
| 음성군 | `33370` |
| 단양군 | `33380` |

증평군은 TAGO 목록에 없음 — `tago_city_code` NULL. SSOT: `town.www/_docs/api_samples/tago_city_codes_chungbuk.json`

| JSON 키 | SNAP 컬럼 | 비고 |
|---|---|---|
| `routeid` | (2단계 입력) | |
| `routeno`, `routetp` | (참조) | |
| `intervaltime` | `avg_bus_interval_min` | **평일** 배차(분) |
| `totalCount` (body) | `bus_route_count` | 1단계 |

**마을별 정밀도 (MVP):**

| 경로 | operation | SNAP 컬럼 |
|---|---|---|
| #6 | `getRouteNoList` / `getRouteInfoIem` | `bus_route_count`, `avg_bus_interval_min` (시/군) |
| **15098534** | `getCrdntPrxmtSttnList` | `nearest_stop_distance_m`, `bus_stops_within_1km` |
| vworld (#7) | geocode | ingest **선행** — `VILLAGE.lat/lng` |
| #6 보조 | `getRouteAcctoThrghSttnList` | 500m~1km 보강 (시/군 캐시) |

**1km 산출 (백엔드 §10-9):**

1. 시/군 `_city_cache`: `getRouteNoList` → `getRouteInfoIem` → `getRouteAcctoThrghSttnList` (노선당 **페이징** 전수) → `nodeid`→(lat,lng) 카탈로그  
2. 마을: `getCrdntPrxmtSttnList` (**페이징**, 고정 ~500m)  
3. `nodeid` 병합 후 Haversine → `nearest_stop_distance_m`, `bus_stops_within_1km`  
4. 좌표 8방향 스윕 **미채택** · 시/군 노선 합계 probe: `tago_route_counts_chungbuk.json` (**1,679**)

---

## ✅ API#6b 버스정류소 — `15098534_stop_nearby.json` (확정 2026-06-21)

**서비스:** `BusSttnInfoInqireService` (15098534)

**URL:** `https://apis.data.go.kr/1613000/BusSttnInfoInqireService/getCrdntPrxmtSttnList`

| Swagger | yaml / `.env.local` | 비고 |
|---|---|---|
| gpsLati * | `PROBE_GPS_LATI` | vworld 마을 위도 |
| gpsLong * | `PROBE_GPS_LONG` | vworld 마을 경도 |
| serviceKey | `BUS_STOP_API_KEY` | 통상 `BUS_ROUTE_API_KEY`와 동일 |

| JSON 키 | SNAP / 용도 | 비고 |
|---|---|---|
| `gpslati`, `gpslong` | `nearest_stop_distance_m` | Haversine(마을↔정류장) 최소값 |
| `nodeid`, `nodenm`, `nodeno` | (참조) | 정류장 식별 |
| `citycode` | (참조) | TAGO 도시코드 (청주 `33010` 등) |
| `totalCount` (body) | (페이징) | **~500m 고정** — 반경 파라미터 없음 |

**SNAP 파생 (§10-9 — 15098534 + 노선 카탈로그 병합):**

```text
# ① 15098534 items (500m) + ② getRouteAcctoThrghSttnList catalog (500m~1km)
# nodeid dedup → Haversine from village(lat,lng)
nearest_stop_distance_m = round(min(distances))
bus_stops_within_1km    = count(d <= 1000 for d in distances)
```

**probe (청주 테스트 좌표 36.637, 127.489):** HTTP 200, `totalCount` 24 (500m), 최근접 `지하상가` ~40m.

---

## API#8 KOSIS → REGION (v1.0 ingest, MVP 미적재) ★ v5.1

| REGION 컬럼 | KOSIS (예시) | 단위 | 갱신 |
|---|---|---|---|
| `birth_rate` | 출생아수 ÷ 시군구 인구 (`INH_1B81A01` 등) | 시군구 | 연간 |
| `daytime_population` | 주간인구지수 (인구총조사 통근·통학) | 시군구 | 5년 |
| `demographic_data_year` | 기준 연도 | — | — |

**v1.0 빈집 sanity check:** `DT_1JU1512` (시군구 공식 빈집) ↔ 읍면동 추정 합산 — `VACANCY_VERIFICATION`  
**ingest:** `region_repository.ingest_kosis_sigungu_demographics()` — tblId는 probe 후 확정

---

## MOIS 3종 — Swagger Parameters (스크린샷 반영)

### 공통

| Swagger | `.env.local` / yaml |
|---|---|
| srchFrYm * | `PROBE_SRCH_FR_YM` (YYYYMM) |
| srchToYm * | `PROBE_SRCH_TO_YM` (3개월 이내) |
| type | `json` |
| pageNo / numOfRows | 1 / 10 |

### API#2 인구·세대 — `GET /selectStdgPpltnHh`

| Swagger | yaml | SNAP |
|---|---|---|
| stdgCd * | `PROBE_STDG_CD` | 조인 (법정동) |
| lv (4) | `"4"` | 통·반 |
| regSeCd (1) | `"1"` | 전체 |
| (응답 TBD) | | `population_total` |
| (응답 TBD) | | `registered_households` |

### API#3 성/연령 — `GET /selectStdgSexdAgePpltn`

**#2와 params 동일** (stdgCd, srchFrYm, srchToYm, lv, regSeCd)

| SNAP | 집계 |
|---|---|
| `population_65plus` | 고령 구간 합 |
| `population_youth` | 청년 연령 합 (팀 정의) |

Response: `만0~9세남자` … `만100세이상여자`

### API#4 인구이동 — `GET /selectPpltnDataStus`

| Swagger | yaml | 비고 |
|---|---|---|
| mvinAdmmCd * | `PROBE_MVIN_ADMM_CD` | **행정기관코드** |
| mvtAdmmCd * | `PROBE_MVT_ADMM_CD` | 전출지 (전국=Swagger Execute 값) |
| lv (3) | `"3"` | 읍·면·동 |
| regSeCd | **없음** | |

`net_youth_migration` = 청년 `만N세` 합산, 전입−전출

> Execute 성공 후 `url` 경로가 다르면 `endpoints.yaml`의 `url`만 교체

---

## 테스트 좌표 (충북·청주)

| 변수 | 값 |
|---|---|
| `PROBE_SIGUNGU_CODE` | `43111` |
| `PROBE_BJDONG_CD` | `10100` |
| `PROBE_BUS_CITY_CODE` | `33010` |
| `PROBE_STDG_CD` | `4311110100` (법정동, #2·#3) |
| `PROBE_SRCH_FR_YM` / `PROBE_SRCH_TO_YM` | `202504` (동일월 OK) |
| `PROBE_MVIN_ADMM_CD` | `4311152500` (#4 전입, 중앙동 행정기관코드) |
| `PROBE_MVT_ADMM_CD` | `1100000000` (#4 전출, Swagger 기본·서울) |
