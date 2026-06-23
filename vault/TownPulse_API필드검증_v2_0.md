# TownPulse — 공공API 필드 재검증 체크리스트 v2.0

> **목적:** 승인된 API 응답 JSON 키 ↔ SNAP/REGION 컬럼 매핑을 **실호출 근거**로 확정  
> **전제:** 개발계정 승인 완료 (2026-06-19 ~ 2028-06-19) — 스크린샷 6종 기준  
> **산출물:** `town.www/_docs/api_samples/*.json` + 아래 매핑표 ✅ 체크 → ERD·개발정의서 §10 반영

---

## 1. 재검증이 필요한 이유

| 한계 | 설명 |
|---|---|
| DCAT / schema.org | 한글 개념 설명만 — JSON 키 이름 없음 |
| 기존 문서 ✅ 표기 | API#2 등은 화면 캡처 기준 — **키 Encoding·파라미터 변경** 가능 |
| API#4 | `net_youth_migration` **직접 필드 없음** — 연령대 합산·전입/전출 집계 필요 |

**DB 없이 1~2단계로 컬럼 확정 가능.** Neon ingest는 백엔드 STEP 1 이후.

---

## 2. 승인 API ↔ SNAP 매핑 (스크린샷 6종)

| # | 승인 서비스 | dataset | SNAP/REGION 컬럼 | 문서상 상태 | 우선순위 |
|---|---|---|---|---|---|
| 1 | 법정동별 주민등록 인구 및 세대현황 | [15108071](https://www.data.go.kr/data/15108071/openapi.do) | `population_total`, `registered_households` | ✅ (재확인) | ★1 |
| 2 | 법정동별 성/연령별 주민등록 인구수 | [15108074](https://www.data.go.kr/data/15108074/openapi.do) | `population_65plus`, `population_youth` | ✅ 확정 | ★2 |
| 3 | 지역별 인구이동 현황 | [15108093](https://www.data.go.kr/data/15108093/openapi.do) | `net_youth_migration` (파생) | ✅ 확정 | ★3 |
| 4 | 건축HUB 건축물대장정보 | Swagger | `residential_buildings` | ✅ 요청·응답 확정 | ★4 |
| 5 | 버스노선 (BusRouteInfoInqireService) | [15098529](https://www.data.go.kr/data/15098529/openapi.do) | `bus_route_count`, `avg_bus_interval_min` | ✅ 확정 (2단계) | ★5 |
| 5b | 버스정류소 (BusSttnInfoInqireService) | [15098534](https://www.data.go.kr/data/15098534/openapi.do) | `nearest_stop_distance_m` 등 (파생) | ✅ probe 확정 (2026-06-21) | ★5b |

**스크린샷에 없지만 §9 스펙 포함:** API#5 재정자립도, API#7 vworld, API#8 KOSIS — 별도 키 있으면 동일 절차.

> **구 API#7 (TAGO 버스노선):** #6과 동일 서비스 통합.  
> **15098534:** 별도 활용신청 — `BUS_STOP_API_KEY` (통상 `BUS_ROUTE_API_KEY`와 동일).

---

## 3. 실행 절차 (백엔드 없이)

### Step 0 — 환경

```powershell
cd town.www
# town.www/.env.local 에 data.go.kr 인증키 + PROBE_* 충북 테스트 좌표 입력
```

### Step 1 — Swagger에서 URL 복사

각 포털 → **활용 명세 → Swagger UI → Try it out → Execute**

- Request URL (base + path) → `town.www/scripts/api_probe/endpoints.yaml` 의 `url`
- Query Parameters → `params` (serviceKey는 `${...}` 유지)
- `enabled: true` 로 변경

### Step 2 — 프로브 실행

```powershell
cd scripts\api_probe
pip install -r requirements.txt
python probe.py --list-keys
python probe.py --id 15108071_household
```

→ `town.www/_docs/api_samples/15108071_household.json` 저장

### Step 3 — 매핑표 작성 (아래 §4)

### Step 4 — 정의서 반영

- `TownPulse_ERD_MVP_v6_1.md` 검증 상태 표 갱신
- `TownPulse_백엔드_MVP_개발정의서_v9_5.md` §5-3⑥·§8·§9·§9-5·§10(§10-8-1·§10-8b·§10-9)·§11-1b·§12-1b·§12-1c·§12-1d·§9-3-1

---

## 4. API별 검증 시트

### API#2 — 인구·세대 (15108071) ★ 기준선

**SNAP:** `population_total`, `registered_households`  
**조인키:** 응답 `법정동코드` ↔ `REGION.legal_dong_code`

| 검증 항목 | 기대 | 실제 JSON 키 | ✅ |
|---|---|---|---|
| 총인구 | integer | | ☐ |
| 세대수 | integer | | ☐ |
| 법정동코드 | 10자리 | | ☐ |
| 행정기관코드 | nullable·조인 금지 | | ☐ |
| 통계년월 | YYYYMM | | ☐ |

**샘플:** `town.www/_docs/api_samples/15108071_household.json`

---

### API#3 — 성/연령별 (15108074)

**SNAP:** `population_65plus`, `population_youth`

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| URL | `stdgSexdAgePpltn/selectStdgSexdAgePpltn` | probe 200 | ✅ |
| 연령 필드 | 10세 구간 | `male20AgeNmprCnt` … `feml100AgeNmprCnt` | ✅ |
| 65+ 합산 | 70세+ 구간 합 | `male/feml 70,80,90,100` | ✅ |
| 청년 (20~39) | 20·30 구간 합 | `male/feml 20,30` | ✅ |
| 법정동코드 | `stdgCd` | `4311110100` | ✅ |
| 통·반 집계 | lv=4 SUM | 10건 → stdgCd 합산 | ✅ |

**샘플:** `town.www/_docs/api_samples/15108074_age.json`

---

### API#4 — 인구이동 (15108093) ✅ v6.0 집계 확정

**SNAP:** `net_youth_migration` (**파생** — SSOT: 백엔드 §10-8-1)

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| URL | `ppltnDataStus/selectPpltnDataStus` | probe 200 | ✅ |
| mvinAdmmCd / mvtAdmmCd | **둘 다 필수** (행정기관코드) | `4311152500` / `1100000000` | ✅ |
| `lv` | `"3"` (읍·면·동) | endpoints.yaml | ✅ |
| srchFrYm / srchToYm | YYYYMM | `202504` | ✅ |
| 연령 필드 | 만 N세 단일 | `male28AgeNmprCnt` 등 | ✅ |
| `mvinAdmmCd` 해석 | `emd_code` 또는 API#2 `admmCd` | ≠ `legal_dong_code` | ✅ |
| net = 전입 − 전출 | 시/도 17개×2 스윕, 20~39세 | §10-8-1 | ✅ |
| 배치 | 3chunk×76동, ~2,584회/일 | §10-7 | ✅ |

**집계식 (확정):**

```
admm_cd = REGION.emd_code or mode(API#2.admmCd where stdgCd=legal_dong_code)
youth_ages = range(20, 40)
total_in  = sum(_sum_youth_count(mvin=admm_cd, mvt=sido_admm_cd(s)) for s in SIDO_CODES)
total_out = sum(_sum_youth_count(mvin=sido_admm_cd(s), mvt=admm_cd) for s in SIDO_CODES)
net_youth_migration = total_in - total_out
```

**샘플:** `town.www/_docs/api_samples/15108093_migration.json` (서울 강남→청주 중앙동, male28=1)

---

### API#1 — 건축HUB ✅ v5.3 화이트리스트 확정

**SNAP:** `residential_buildings` = `mainPurpsCdNm` 화이트리스트 COUNT (전 페이지 순회) + 비표준값 **unmatched 감사 로깅**

**URL:** `https://apis.data.go.kr/1613000/BldRgstHubService/getBrTitleInfo`

**화이트리스트 (정확매칭 7종, SSOT: 백엔드 §10-8b-1):**

| 포함 | 제외 (의도적) |
|---|---|
| 단독주택, **다중주택**, 다가구주택, 공동주택, 아파트, 연립주택, 다세대주택 | 공관, **기숙사**, 오피스텔 |

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| 요청 `sigunguCd` | `REGION.sigungu_code` (5자리) | `43111` | ✅ |
| 요청 `bjdongCd` | `legal_dong_code[5:10]` | `10100` | ✅ |
| `bun`/`ji` | 생략 가능 (법정동 전체) | probe 생략 | ✅ |
| 페이징 | `numOfRows`+`pageNo`→`totalCount` | `building_hub_title.json` | ✅ |
| 응답 `mainPurpsCdNm` | 7종 화이트리스트 COUNT | probe 200 | ✅ |
| unmatched 로깅 | 비표준·비어있지 않은 값 빈도 | §10-8b 설계 | ✅ |

**샘플:** `town.www/_docs/api_samples/building_hub_title.json` (10건: 단독주택 5, 제1종근린 3, 제2종근린 2 — 기숙사·다중주택 미출현)

---

### API#8 — KOSIS → REGION (시군구, v1.0 ingest) ★ v5.1

**REGION:** `birth_rate`, `daytime_population`, `demographic_data_year` — **MVP TVI 미사용·미적재**

| 지표 | KOSIS (예시 tblId) | 단위 | 갱신 | MVP |
|---|---|---|---|---|
| 조출생률 | `INH_1B81A01` (출생아수) ÷ 시군구 인구 | 시군구 | 연간 | v1.0 ingest |
| 주간인구지수 | 인구총조사 통근·통학 | 시군구 | 5년 | v1.0 ingest |
| 빈집 검증(v1.0) | `DT_1JU1512` | 시군구 | 연간 | `VACANCY_VERIFICATION` |

> 법정동(읍면동) 단위 직접 공표 없음 — `fiscal_self_reliance`와 동일 패턴.

---

### API#6 — 버스노선 (BusRouteInfoInqireService)

**SNAP:** `bus_route_count`, `avg_bus_interval_min`

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| 서비스 URL | `BusRouteInfoInqireService` | probe 200 | ✅ |
| 1단계 `getRouteNoList` | totalCount, routeid | 청주 118건 | ✅ |
| 2단계 `getRouteInfoIem` | intervaltime | 105번 40분 | ✅ |
| cityCode | TAGO 도시코드 | `33010` (43111 ❌) | ✅ |
| TAGO 중복신청(#7) | 동일 응답 | 통합 — 폴백 불필요 | ✅ |
| `REGION.tago_city_code` | 시/군별 매핑 | getCtyCodeList **10건**(충북, 증평 제외) | ✅ probe → `tago_city_codes_chungbuk.json` |

**2단계:** ① `cityCode`→routeId ② routeId→`intervaltime`

**샘플:** `town.www/_docs/api_samples/bus_route_primary.json`, `bus_route_detail.json`, `tago_city_codes.json`, `tago_city_codes_chungbuk.json`

---

### API#6b — 버스정류소 (15098534) **MVP**

**SNAP:** `nearest_stop_distance_m`, `bus_stops_within_1km` (+ §9 `bus_interval_score` 0점 조건)

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| URL | `getCrdntPrxmtSttnList` | `BusSttnInfoInqireService` | ✅ |
| gpsLati / gpsLong | vworld 마을 좌표 | `PROBE_GPS_*` (36.637, 127.489) | ✅ |
| 활용승인 | 2026-06-21~2028-06-21 | 포털 **[승인]** | ✅ |
| probe HTTP | 200 | **200** (이전 403 → 통과) | ✅ |
| `resultCode` | `00` | `00` + `NORMAL SERVICE.` | ✅ |
| `nodeid`, `nodenm`, `gpslati`, `gpslong` | 정류장 식별·좌표 | 10건/페이지, `totalCount` 24 (500m) | ✅ |
| `citycode`, `nodeno` | (참조) | TAGO citycode·정류장번호 | ✅ |

**1km 산출 (§10-9 SSOT):** `getCrdntPrxmtSttnList`(고정 ~500m, 페이징) + `getRouteAcctoThrghSttnList` 시/군 카탈로그(노선당 페이징) → `nodeid` 병합 → Haversine. 좌표 8방향 스윕 **미채택**.

| 검증 항목 | 기대 | 실제 | ✅ |
|---|---|---|---|
| 1km 알고리즘 | §10-9 문서화 | 노선카탈로그+15098534 병합 | ✅ v1.1 |
| 시/군 노선 수 | probe | `tago_route_counts_chungbuk.json` 합계 **1,679** | ✅ |

**샘플:** `15098534_stop_nearby.json`, `bus_route_stops.json`, `tago_route_counts_chungbuk.json`

## 5. 공통 테스트 좌표 (충북)

`town.www/.env.local` 의 `PROBE_*` — **API#2 첫 호출 결과**로 법정동코드·통계년월 확정 권장.

| 변수 | 초기값 | 용도 |
|---|---|---|
| `PROBE_SIGUNGU_CODE` | `43111` | 청주시 상당구 (예시) |
| `PROBE_LEGAL_DONG_CODE` | `4311110100` | Swagger/응답으로 교체 |
| `PROBE_STATS_YM` | `202501` | 최근 공표월 (매월 2일 이후) |

---

## 6. 완료 기준

- [ ] 6종 API 각 1건 이상 `town.www/_docs/api_samples/` JSON 보관
- [ ] §4 매핑표 전 항목 ✅
- [ ] API#4 `net_youth_migration` — §10-8-1 시/도 스윕·3일 분할 배치
- [ ] `birth_rate`, `daytime_population` — **REGION + KOSIS #8 (시군구)** 확정, MVP 미적재
- [ ] ERD v6.0 + 개발정의서 v9.0 §10-8-1·§10-8b·§10-9 검증 상태 일치

---

## 7. 트래픽 주의

개발계정 **10,000회/일** — 프로브는 API당 1~2회, 충북 전체 루프는 백엔드 배치 구현 후.

---

*© 2026 Pulse Lab | API 필드 검증 워크플로*
