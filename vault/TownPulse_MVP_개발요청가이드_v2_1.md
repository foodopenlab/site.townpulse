# TownPulse — MVP 단계별 AI 개발 요청 가이드 v2.1

> 대상: 2026 충청북도 공공데이터·AI 활용 창업경진대회 제출 버전  
> 목표: 충북 228개 읍면동 히트맵 + TVI 산출 + AI 처방 3종 + PDF 리포트 라이브 데모  
> **제출:** 2026-06-26 · **코드·문서 freeze:** 2026-06-25  
> 정의서: `TownPulse_백엔드_MVP_개발정의서_v9_5.md` · `TownPulse_프론트엔드_개발정의서_v2_3.md` · `TownPulse_ERD_MVP_v6_1.md` · `TownPulse_와이어프레임_MVP_v1_0.md`

---

## 이 가이드의 목적

백엔드만 먼저 완성한 뒤 프론트를 붙이면 **경로·필드명·식별자** 불일치로 연동 오류가 자주 난다.  
본 가이드는 **「API 계약 확정 → 백엔드 1엔드포인트 → 프론트 1화면 → 연동 게이트」** 를 반복하는 **웨이브형** 순서다.

```
계약(§0) → 인프라 → [인증 GATE] → [대시보드·지도 GATE] → [마을상세 GATE]
         → [처방 GATE] → [리포트 GATE] → 배치(실데이터) → 배포 E2E
```

---

## 전달 원칙

| 단계 유형 | 첨부 파일 |
|---|---|
| 백엔드 | `TownPulse_백엔드_MVP_개발정의서_v9_5.md` + `TownPulse_ERD_MVP_v6_1.md` |
| 프론트 | `TownPulse_프론트엔드_개발정의서_v2_3.md` + `TownPulse_와이어프레임_MVP_v1_0.md` |
| API 필드·배치 | `TownPulse_API필드검증_v2_0.md` + `town.www/_docs/api_samples/FIELD_MAPPING_v2_0.md` |
| 연동 게이트 | **해당 STEP의 「연동 게이트」표** — curl + 브라우저 확인을 AI에게 시키지 말고 **직접 실행** |

요청문은 **무엇을 만들지**만 짧게 쓴다. 스펙은 첨부 정의서가 SSOT.

### MVP 제출 전 실데이터 적재 (§10-7)

개발계정 **10,000회/일** — API#4 migration(7,752회)은 **3일 분할** 필수.

| 일자 | Admin 트리거 | 내용 |
|---|---|---|
| **06-23** | `POST …/sync/collect-core` | vworld·pop#2#3·building·transport·statistics |
| **06-23** | `…/sync/migration/0` | API#4 chunk 0 (76 법정동) |
| **06-24** | `…/sync/migration/1` | chunk 1 |
| **06-25** | `…/sync/migration/2` | chunk 2 |
| **06-25 PM** | `…/sync/finalize` | `recalculate_all()` → TVI |

REGION 시드에 **`emd_code`**(행정기관코드) 포함 — API#4 `mvinAdmmCd` 해석 1순위.

---

## §0. 연동 계약 (모든 STEP 전에 합의)

### 0-1. URL·prefix

| 항목 | 값 |
|---|---|
| API prefix | `/api/townpulse/` |
| 프론트 base | `NEXT_PUBLIC_API_BASE_URL` + 위 prefix |
| CORS | `https://townpulse.site`, `http://localhost:3000` |

### 0-2. 식별자 (연동 오류 1순위)

| 필드 | 형식 | URL | API body/path |
|---|---|---|---|
| `village_code` | 10자리 문자열 `"4300025000"` | `/map/[villageCode]` | 오케스트레이터 경로 |
| `village_id` | UUID | — | `prescription-results`, `snap/*` |
| `prescription_result_id` | UUID | — | SSE `/stream` |

**규칙:** 화면 URL은 항상 `village_code`. `village-detail` 1회 호출로 `village_id` 확보 후 처방 API 사용.

### 0-3. 화면 ↔ API 매핑 (SSOT)

| 화면 | Method | Path | 프론트 타입 (§13) |
|---|---|---|---|
| D-01 로그인 | POST | `/users/login` | `auth.ts` |
| D-02 대시보드 | GET | `/dashboard/summary` | `DashboardSummary` |
| D-03 지도 목록 | GET | `/dashboard/map/villages` | `VillageListItem[]` |
| D-03 요약 카드 | GET | `/dashboard/map/villages/{village_code}` | `VillageMapSummary` |
| D-04 마을 상세 | GET | `/village-detail/{village_code}` | `VillageDetail` |
| D-05 처방 목록 | GET | `/prescription-results/by-village/{village_id}` | `PrescriptionList` |
| D-05 처방 생성 | POST | `/prescription-results` | body: `{ village_id }` |
| D-05 Gemini SSE | GET | `/prescription-results/{id}/stream?token=` | EventSource |
| D-06 리포트 | POST | `/report-data/{village_code}` | `ReportBuildRequest` |

> **사용 금지 (구 v1):** `/map/villages`, `/prescription/chat`, `/report/generate`, `/api/auth/login`

### 0-4. 공통 응답 규칙

| 항목 | 규칙 |
|---|---|
| `tvi_grade` | `"danger"` \| `"warning"` \| `"safe"` (영문) |
| 날짜 | ISO 8601 UTC |
| JWT | Header `Authorization: Bearer` · SSE만 `?token=` |
| AI | **Gemini** (`prescription_result.ai_description`) — Claude 아님 |
| 교통 공백 | 확정 공백만 `bus_interval_score === 0` ↔ `transport_gap_count` · `bus_route_count=null`은 제외 ★ v9.4 |

### 0-5. 데모 시드 (연동 테스트용 고정값)

| 항목 | 값 |
|---|---|
| 테스트 마을 | 단양군 영춘면 `village_code=4300025000` |
| 로그인 | `POST /users/login` — **내부 QA 전용** (`town.www/.env.local` `QA_SEED_*`, 문서에 평문 금지) |
| 데모 진입 | `POST /users/demo/token` — 방문자 자동 발급, 로그인 화면 스킵 (§12-1b) |
| 기대 TVI 데모 | ~12점, `danger` (시드 기준) |

---

## 웨이브 1 — 인프라 (병렬 가능, 연동 전)

### STEP 1-A — 백엔드 뼈대 + DB

**요약:** v8 아키텍처 뼈대, ERD **18테이블**, NeonDB, matrix 7파일.

**요청 예시:**
```
TownPulse_백엔드_MVP_개발정의서_v9_5 §3·§8·§9·§9-3-1·§9-5·§10·§11-1b·§12-1b·§12-1c·§15을 참고해서:
- townpulse-api/ 프로젝트 구조 (shared/ 없음, core/matrix/ 7파일)
- adapter/outbound/orm/ ERD 18테이블 ORM
- alembic 초기 마이그레이션 + db_init
- main.py (lifespan, CORS, townpulse_router 빈 집계)
- `town.www/.env.local` (PROBE_*, 공공API 키, QA_SEED_*, DATABASE_URL, GEMINI 등)
- 충북 228 village 시드 + prescription_type 5종 + dispatch_rule 시드
  village.emd_code = village_code (10자리), lat/lng 더미
```

**완료 기준:**
- `alembic upgrade head` 성공
- `SELECT COUNT(*) FROM village` → 228
- `uvicorn main:app` + `/docs` 접근

---

### STEP 1-B — 프론트 뼈대 + 테마

**요약:** Next.js 14, **라이트 기본** 테마, Axios·Zustand·타입 골격.

**요청 예시:**
```
TownPulse_프론트엔드_개발정의서_v2_1 §1·§3·§12·§13을 참고해서:
- Next.js 14 + Tailwind darkMode:'class' + next-themes
- app/globals.css (:root 라이트 / .dark 다크)
- app/layout.tsx ThemeProvider defaultTheme="light"
- components/theme/theme-toggle.tsx
- lib/api/client.ts, lib/types/* (§13 타입 그대로)
- lib/utils/tvi.ts, format.ts
- components/ui/Badge, LoadingSpinner, ErrorMessage
```

**완료 기준:**
- `npm run dev` 오류 없음
- 첫 화면 **라이트** · Moon 토글 → 다크 전환

---

## 웨이브 2 — 인증 연동

### STEP 2-A — 백엔드 USER + JWT

**요약:** `USER` 도메인 12파일 프랙탈 + Trinity JWT + QA 시드 (§12-1c).

**요청 예시:**
```
v9 §6·§7·§12-1c: user_router 12파일 프랙탈
- POST /api/townpulse/users/login  (org_id + password → access_token, org_name, user_name)
- GET  /api/townpulse/users/me
- core/matrix/grid_trinity_hacker_mixin.py — JWT Depends
- town.www/scripts/seed/seed_qa_account.py — STEP 1 직후 1회 (QA_SEED_*)
```

**완료 기준:**
- `POST /users/login` → `access_token` JSON
- 토큰 없이 보호 API → 401

---

### STEP 2-B — 프론트 D-01 로그인 + 레이아웃

**요청 예시:**
```
와이어프레임 D-01 + 프론트 §4·§11:
- app/(auth)/login/page.tsx
- app/(dashboard)/layout.tsx (JWT 가드)
- Header + Sidebar + BottomNav + ThemeToggle
- lib/api/auth.ts → POST /api/townpulse/users/login
- lib/store/authStore.ts
```

---

### 🔗 GATE 1 — 인증 연동

| 확인 | 방법 |
|---|---|
| 데모 토큰 200 | `curl -X POST localhost:8000/api/townpulse/users/demo/token` → `access_token`, `scope=demo_readonly` |
| 데모 GET 통과 | 위 토큰으로 `GET /api/townpulse/dashboard/summary` → 200 |
| 데모 POST 차단 | 데모 토큰으로 `POST /api/townpulse/prescription-results` → **403** |
| QA 로그인 200 | `curl -X POST localhost:8000/api/townpulse/users/login -H "Content-Type: application/json" -d "{\"org_id\":\"$QA_SEED_ORG_ID\",\"password\":\"$QA_SEED_PASSWORD\"}"` (`town.www/.env.local` 값) |
| 프론트 데모 진입 | `/` 접속 → `ensureDemoSession()` → `/dashboard` (로그인 폼 스킵) |
| 401 리다이렉트 | 토큰 삭제 후 `/dashboard` → `/login` (QA 세션 테스트 시) |
| CORS | 프론트 `localhost:3000` → API preflight 통과 |

**통과 전 다음 웨이브 금지.**

---

## 웨이브 3 — 대시보드 + 지도

### STEP 3-A — 백엔드 DASHBOARD_ORCHESTRATOR

**요약:** 화면용 집계 — **map_village_router 아님**.

**요청 예시:**
```
v8 §5-1 #19, §7 오케스트레이터, §10 Phase 10-B:
- dashboard_orchestrator_* 12파일 프랙탈
- GET /api/townpulse/dashboard/summary
- GET /api/townpulse/dashboard/map/villages?grade=&sigun=
- GET /api/townpulse/dashboard/map/villages/{village_code}
응답 필드 = 프론트 §13 VillageListItem, DashboardSummary, VillageMapSummary
transport_gap_count = bus_interval_score==0 마을 수
```

**완료 기준:**
- `summary`: `danger_count+warning_count+safe_count == total_villages`
- `map/villages`: 228건, 각 항목 `village_code`, `lat`, `lng`, `tvi_grade`

---

### STEP 3-B — 프론트 D-02 + D-03

**요청 예시:**
```
와이어프레임 D-02·D-03 + 프론트 §7.2:
- lib/api/dashboard.ts (summary + map/villages)
- dashboard/page.tsx — StatCard 4개(교통공백 포함)
- map/page.tsx — VillageMap dynamic import
- MapFilters (tvi/vacant/elderly/bus/stop_access)
- VillageSummaryCard
- public/geojson/chungbuk_emd.geojson — emd_code ↔ village_code 조인
```

---

### 🔗 GATE 2 — 대시보드·지도 연동

| 확인 | 백엔드 | 프론트 |
|---|---|---|
| 카드 4개 수치 | `GET /dashboard/summary` | D-02 표시 일치 |
| 히트맵 228 | `GET /dashboard/map/villages` | 폴리곤 색상 danger/warning/safe |
| 클릭 요약 | `GET .../map/villages/4300025000` | 요약 카드 + 정류장 거리 필드 |
| 필드명 | `village_code` not `emdCode` | Network 탭 JSON 키 = §13 타입 |

**통과 전 D-04 금지.**

---

## 웨이브 4 — 마을 상세

### STEP 4-A — 백엔드 VILLAGE_DETAIL_ORCHESTRATOR

**요청 예시:**
```
v8 §5-1 #20, Phase 10-C:
- village_detail_orchestrator_* 12파일
- GET /api/townpulse/village-detail/{village_code}
- SNAP×4 + TVI + prescription 상위 2 asyncio.gather
- 응답: village_id, village_code, 5지표(정류장 포함), snap_transport, prescriptions_preview
```

**완료 기준:**
- `4300025000` → `village_id` UUID 포함
- `nearest_stop_distance_m`, `bus_stops_within_1km`, `transport_gap` 필드 존재

---

### STEP 4-B — 프론트 D-04

**요청 예시:**
```
와이어프레임 D-04 + 프론트 §5-4:
- lib/api/village.ts → village-detail
- map/[villageCode]/page.tsx
- IndicatorCards 5개 (정류장 접근 카드 포함)
- RiskBarChart, ExtinctionProbability, 처방 미리보기 2건
```

---

### 🔗 GATE 3 — 마을 상세 연동

| 확인 | 방법 |
|---|---|
| `village_id` 확보 | D-04 Network → UUID 복사 |
| 5지표 표시 | 빈집·고령·배차·**정류장**·인구 |
| 미리보기 2건 | `prescriptions_preview` 또는 빈 배열 처리 |
| breadcrumb | `/map` → `/map/4300025000` |

---

## 웨이브 5 — AI 처방

### STEP 5-A — 백엔드 PRESCRIPTION_RESULT (+ DISPATCH_RULE 등)

**요청 예시:**
```
v8 §6 prescription_result_router, §9 TVI→dispatch:
- prescription_result_* 12파일 + dispatch_rule, budget_unit_price, prescription_type 연동
- POST /api/townpulse/prescription-results  { village_id }
- GET  /api/townpulse/prescription-results/by-village/{village_id}
- GET  /api/townpulse/prescription-results/{id}/stream?token=  (Gemini SSE)
- prescription_result_repository 내부 Gemini (Keymaker·Smith 경유)
응답 PrescriptionItem: id, rank, title, budget_min/max, tvi_gain_*, fund_applicable, timeline
```

**완료 기준:**
- POST 후 3건 `priority_rank` 1·2·3
- SSE 텍스트 청크 + `[DONE]` 또는 연결 종료

---

### STEP 5-B — 프론트 D-05

**요청 예시:**
```
와이어프레임 D-05 + 프론트 §9:
- lib/api/prescription.ts (by-village, generate, createPrescriptionStream)
- prescription/[villageCode]/page.tsx
- village-detail로 village_id 로드 → 처방 fetch
- PrescriptionCard ×3, Gemini 스트림 영역, QuickQuestionBar(설명 다시보기)
- 구 /prescription/chat 사용 금지
```

---

### 🔗 GATE 4 — 처방 연동

| 확인 | 방법 |
|---|---|
| village_id 경로 | `by-village/{uuid}` not `{village_code}` |
| SSE token | EventSource URL에 `?token=` (Header 불가) |
| 1순위 id | 스트림 URL의 UUID = 카드 `id` |
| 예산 단위 | `budget_min/max` 만원 — `formatBudget` |

---

## 웨이브 6 — 리포트

### STEP 6-A — 백엔드 REPORT_ORCHESTRATOR

**요청 예시:**
```
v8 §5-1 #21, Phase 10-D:
- report_orchestrator_* — village_detail 재사용 + budget
- POST /api/townpulse/report-data/{village_code}
- report_repository — REPORT 테이블 이력 (format: pdf)
```

---

### STEP 6-B — 프론트 D-06

**요청 예시:**
```
와이어프레임 D-06 + 프론트 §10:
- lib/api/report.ts → report-data
- report/[villageCode]/page.tsx
- ReportOptions, ReportPreview, lib/utils/pdf.ts
- PDF 미리보기는 bg-card (라이트·다크 대응)
```

---

### 🔗 GATE 5 — 리포트 연동

| 확인 | 방법 |
|---|---|
| POST body | `include_risk_analysis` 등 snake_case |
| PDF 다운로드 | html2canvas → A4 |
| REPORT 행 | POST 후 DB `report` 1건 (선택) |

---

## 웨이브 7 — 공공데이터 배치 (데모 전)

### STEP 7 — 백엔드 PUBLIC_DATA_SYNC + Repository ingest

**요약:** v8 **pipeline/ 폴더 없음** — `{table}_repository.ingest_*`.

**요청 예시:**
```
v9.0 §10-8-1·§10-8b·§10-9, ERD v6.0, FIELD_MAPPING_v2_0.md:
- public_data_sync_orchestrator_* 12파일 + sync_job ORM
- snap_*_repository.ingest_from_public_api / ingest_for_village
- `snap_transport_repository` — §10-9 `_city_cache` + `_aggregate_stop_access` (15098534+노선카탈로그)
- 순서: vworld geocode → population/building/statistics → transport(15098534) → tvi recalculate_all
- POST /api/townpulse/admin/sync/trigger
- API 키 없으면 Mock/시드 유지 (대회 데모는 시드만으로도 GATE 2~5 통과 가능)
```

**완료 기준:**
- `collect_all` 후 SNAP_TRANSPORT에 `nearest_stop_distance_m` 채움 (키 있을 때)
- TVI_SCORE 재계산

**[OPTIONAL stretch — §12-1d]:**
- [ ] `recalculate_all()` 1회차 완료 후 `town.www/scripts/seed/seed_all_prescriptions.py` (Railway URL 또는 localhost)
- [ ] 로그 `실패 0` · 데모 토큰으로 임의 마을 1~2곳 403 없음

> **팁:** STEP 1 시드만으로 UI 연동 먼저 끝내고, STEP 7은 실데이터 데모 직전에 수행. **제출 E2E는 영춘면 2~3곳 QA 사전생성으로 충분.**

---

## 웨이브 8 — 나머지 백엔드 도메인 (병렬·후순위)

MVP 데모에 **직접 노출 안 되는** ERD 도메인은 GATE 5 이후 채운다.

| 우선순위 | 도메인 | 비고 |
|---|---|---|
| 중 | `tvi_score_router` | 오케스트레이터가 내부 사용 |
| 중 | `region_router`, `village_router` | 시드·관리 |
| 낮 | `organization`, `subscription` | SaaS |
| 낮 | `snap_*` 개별 조회 API | 심사용 원본 확인 |

---

## 웨이브 9 — 모바일 + 마무리

### STEP 9-A — 프론트 M-01~M-05

```
와이어프레임 §4 + 프론트 §4-3:
- BottomNav, 375px 레이아웃, StatCard 2×2
- 지도 터치 줌, 테마 토글 모바일 Header
```

### STEP 9-B — 배포 (Railway)

| 순서 | 작업 | 완료 기준 |
|---|---|---|
| 1 | **Railway** Docker + Neon `DATABASE_URL` + §14 env | `/docs` HTTPS (`*.up.railway.app` 또는 `api.townpulse.site`) |
| 2 | Vercel + `townpulse.site` | `NEXT_PUBLIC_API_BASE_URL` → Railway |
| 3 | `seed_qa_account` (Railway env `QA_SEED_*`) | GATE 1 QA 로그인 200 |
| 4 | **E2E 데모** | 아래 시나리오 1회 완주 |
| 5 | **[OPTIONAL]** `seed_all_prescriptions` | §12-1d — 6/25 finalize 이후 |

---

## E2E 데모 시나리오 (최종 GATE)

```
1. https://townpulse.site 로그인 (라이트 UI)
2. D-02 — 교통공백 37곳 등 카드 표시
3. D-03 — 영춘면 클릭 → 정류장 거리 요약
4. D-04 — TVI + 5지표 + 처방 미리보기
5. D-05 — 처방 3건 + Gemini 스트림
6. D-06 — PDF 다운로드
7. (선택) 다크 토글 후 D-02 가독성 확인
8. **[OPTIONAL]** 영춘면 외 임의 마을 1~2곳 클릭 → 처방 정상 (§12-1d 선생성 검증)
```

---

## 연동 오류 방지 체크리스트

```
[ ] API prefix /api/townpulse/ 양쪽 동일
[ ] village_code(URL) vs village_id(API) 혼동 없음
[ ] tvi_grade 영문 danger|warning|safe
[ ] SSE ?token= 쿼리 (Authorization 아님)
[ ] CORS origin townpulse.site + localhost:3000
[ ] 구 엔드포인트(/map/villages, /prescription/chat) 미사용
[ ] Gemini (Claude 코드·env 제거)
[ ] transport_gap_count ↔ bus_interval_score 규칙 일치
[ ] 프론트 §13 타입 ↔ 백엔드 Schema 필드명 1:1
[ ] 첫 테마 라이트 · townpulse-theme localStorage
```

---

## MVP 완료 기준

```
[ ] GATE 1~5 전부 통과
[ ] E2E 데모 시나리오 완주
[ ] https://townpulse.site · https://api.townpulse.site/docs
[ ] 228 읍면동 히트맵 + 영춘면 상세 5지표
[ ] 처방 3건 + Gemini SSE
[ ] PDF 리포트
[ ] (목표) 공공API 8종+15098534 ingest 또는 시드+Mock 문서화
```

---

## 부록 — STEP 요약 타임라인

| 순서 | STEP | 담당 | 연동 GATE |
|---|---|---|---|
| 0 | §0 계약 숙지 | 팀 | — |
| 1 | 1-A DB + 1-B 프론트 뼈대 | BE / FE | — |
| 2 | 2-A USER + 2-B 로그인 | BE → FE | **GATE 1** |
| 3 | 3-A Dashboard Orch + 3-B D-02·D-03 | BE → FE | **GATE 2** |
| 4 | 4-A Village Detail + 4-B D-04 | BE → FE | **GATE 3** |
| 5 | 5-A Prescription + 5-B D-05 | BE → FE | **GATE 4** |
| 6 | 6-A Report Orch + 6-B D-06 | BE → FE | **GATE 5** |
| 7 | 7 배치 ingest | BE | — |
| 8 | 8 잔여 도메인 | BE | — |
| 9 | 9 모바일 + 배포 E2E | FE / Ops | **E2E** |

---

*© 2026 Pulse Lab | TownPulse MVP 개발 요청 가이드 v2.0 | Confidential*
