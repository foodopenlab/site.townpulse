# TownPulse — 백엔드 MVP 개발정의서

> 서비스명: TownPulse | 충북 마을생존 AI 의사결정 플랫폼
> 버전: MVP v9.5 | 작성일: 2026년 6월 | 팀: Pulse Lab
> **버전 규칙:** 마이너는 **0~9 한 자리**. `vX_9` 다음은 `v(X+1)_0` (예: v8_9→v8_10 금지, **v9_0**으로 메이저 갱신).
> 변경 이력:
> - v3.0 — 아키텍처 리팩터링: inbound mapper, AI 포트 분리, grade_filter Interactor 이동
> - v4.0 — **SRP 완전 준수: 라우터 4개 → 18개 재분리 (ERD 18개 테이블 1:1 대응)**
> - v5.0 — **오케스트레이터 3개 추가 (총 21개 도메인) + VO AOP 분리**
> - v6.0 — **ERD MVP v4 정합: 공공API 5종 가정 → 실연동 9종 확정 반영 (건축HUB·인구3종·재정자립도·버스2종·vworld·kosis) / `registered_households` SNAP_BUILDING→SNAP_POPULATION 이전(SRP 위반 수정) / `fiscal_self_reliance` SNAP_POPULATION→REGION 이전(정규화 위반 수정) / REGION 코드체계 4종(법정동코드·행정동코드·시군구코드·TAGO도시코드) 확정 / TAGO 폴백 2단계 호출 구조 반영 + 구조.md(siliconvalley 하네스) 경계 톨게이트 원칙 정합 — Assembler/Mapper는 체인의 별도 "층"이 아니라 Router·Repository 경계에서만 타입을 갈아입힘을 명문화**
> - v7.0 — **오케스트레이터 프랙탈 구조 복원 (Entity, Output Port 추가 및 Interactor 명칭 *_interactor.py 통일) + 예외적 AI 포트(ai_text_generator_port) 제거 후 prescription_result_port 통합 + AI 모델: Google Gemini API + _memory_repository 제거 (NeonDB 전용) + `shared/` 제거·`core/matrix/` 7파일 체계 확정 (Keymaker·Oracle·Neo·Morpheus·Trinity·Smith)** ★ v7
> - v7.1 — **`adapter/outbound/ai/` 제거 → Gemini 호출을 `prescription_result_repository.py` 내부로 흡수 (12파일 프랙탈 유지)**
> - v8.0 — **`adapter/outbound/pipeline/` 전체 제거 → 공공API·TVI 배치를 각 `{table}_repository.py` private ingest + `core/matrix/` BatchScheduler·PublicDataCollector(9파일 matrix)로 흡수 — Repository outbound 통합 SRP·21×12 프랙탈 완전 정합** ★ v8
> - v8.1 — **4번째 오케스트레이터 `PUBLIC_DATA_SYNC_ORCHESTRATOR` 추가 (총 22×12 프랙탈) — cron·수동 트리거·APScheduler를 Provider로 이동, matrix 배치 2파일 삭제 → matrix 7파일(v7) 복원 + VO `sync_job_type_vo`·`sync_job_status_vo`** ★ v8.1
> - v8.2 — **API#6·#7 버스 통합** — probe로 `BusRouteInfoInqireService` 동일 확인 → **8종 API**, `TAGO_API_KEY` 제거, `tago_city_code`=버스 cityCode 전용 ★ v8.2
> - v8.3 — **SNAP_TRANSPORT MVP = 노선 2단계 + 정류소(15098534)** — `nearest_stop_distance_m`·`bus_stops_within_1km` 컬럼, ingest는 **vworld 좌표 선행** 후 마을 단위 ★ v8.3
> - v8.4 — **`birth_rate`·`daytime_population` SNAP_POPULATION→REGION** (KOSIS #8·시군구·`fiscal_self_reliance` 패턴, MVP 미적재) · **건축HUB 요청 파라미터 확정** (`sigunguCd`+`bjdongCd`+페이징) · v1.0 `VACANCY_VERIFICATION`→KOSIS `DT_1JU1512` 시군구 ★ v8.4
> - v8.5 — **§9 TVI 정규화·시뮬레이션 명문화** — `pop_decline_score` 5지표 min-max 가중합(행안부 **항목** 준용·산식 자체 설계) · `simulate_tvi_gain()` 역산 · 처방별 SNAP 필드 변경표 ★ v8.5
> - v8.6 — **§11-1b Prompt Engineering** — `TOWNPULSE_PRESCRIPTION_PERSONA` 개정(숫자 불변) · `_build_context_prompt()` 서버 조립 · `PrescriptionResultStreamCommand` ID 기반 · Interactor 포트 4종 추가 주입 ★ v8.6
> - v8.7 — **§5-3⑥ TAGO `tago_city_code` 시드** — `getCtyCodeList` probe 확정(충북 10건) · `town.www/scripts/seed/seed_tago_city_code.py` · **§12-1b 공개 데모 모드** — `POST /users/demo/token` 읽기전용 JWT · POST `require_write_scope` ★ v8.7
> - v8.8 — **§9-0 TVI SSOT 경계** — `pop_decline_score`만 min-max · 빈집·교통 선형식 유지 · DRT=배차만(교통 공백 Δ 제한) · 외부 시뮬레이션 수치 비채택 ★ v8.8
> - v8.9 — **§10-9 정류장 1km 알고리즘** — 15098534(500m 고정)+노선 카탈로그(`getRouteAcctoThrghSttnList`) Haversine 병합 · 시/군 `_city_cache` · 좌표 8방향 스윕 미채택 · `tago_route_counts_chungbuk.json` probe ★ v8.9
> - v8.10 — **§10-8b `mainPurpsCdNm` 주거용 화이트리스트 판정 사전** — 별표1 근거 7종(다중주택 추가) · 기숙사·공관·오피스텔 의도적 제외 · `_count_residential_with_audit` unmatched 로깅 ★ v8.10
> - v9.0 — **§10-8-1 `net_youth_migration` 집계** — 시/도 17개 스윕 · `emd_code`/API#2 `admmCd` 해석 · 3일 분할 배치(MVP 제출 6/26) · `collect_all_core`/`collect_migration_chunk`/`finalize_monthly_snap` · **v8_10 이후 메이저 갱신(v9_0)** ★ v9.0
> - v9.1 — **§12-1c USER 로그인·QA 시드 확정** — `townpulse_user.password_hash` · `POST /users/login` 계약(`org_id`=organization.id) · `user_interactor.login` · `require_write_scope` 판정표 · `town.www/scripts/seed/seed_qa_account.py` · 신규 AUTH 도메인 없음(USER+Trinity) ★ v9.1
> - v9.2 — **§12-1d [OPTIONAL] 데모 228마을 처방 선생성** · `seed_all_prescriptions.py` · **§15 Railway 배포**(PaaS, Neon 외부 DB) · 제출 필수는 §12-1b 2~3곳 ★ v9.2
> - v9.3 — **§9-3-1 상대평가 한계·`tvi_delta` 해석** (문서 확정) · EMA/`tvi_norm_state`는 **MVP이후 v4_0** ★ v9.3
> - v9.4 — **§9-4·§10-9-3 증평군(`tago_city_code` NULL) 교통 공백 왜곡 수정** — 15098534 GPS 호출 유지 · `bus_route_count=None` · `calculate_bus_interval_score` 3단계 · 프론트 배지 분리 ★ v9.4
> - v9.5 — **§9-5 처방 시뮬 지역 연동** — INCENTIVE 동적 정착률 γ(교통·청년비율) · SOC_COMPLEX 빈집 비율 연계 `pop_density` — 재정자립도 UI·Delphi/ML은 **MVP이후 v4_0** §1-6 ★ v9.5
> 참고 아키텍처: `titanic-bone.md` + `titanic-bone-improvement.md` (Hexagonal + Clean + DDD + Fractal) · `구조.md`(siliconvalley 형제 앱 하네스 — 경계 톨게이트·프랙탈 네이밍 정합 기준) ★ v8.1
> 참고 데이터 모델: `TownPulse_ERD_MVP_v6_1.md` ★ v9.5
> MVP 이후 로드맵: `TownPulse_백엔드_MVP이후_개발정의서_v4_0.md` ★ v9.5
> API 필드 probe: `TownPulse_API필드검증_v2_0.md` · `town.www/_docs/api_samples/` · `town.www/_docs/api_samples/FIELD_MAPPING_v2_0.md` ★ v9.0
> 배포: **Railway** (MVP) · EC2 대안 | DB: NeonDB (PostgreSQL serverless) | AI: Gemini API
> 도메인: `api.townpulse.site`

---

## ⚠️ 전체 주의사항 — AI 코딩 시 반드시 확인

```
❌ RDS 아님 → NeonDB (PostgreSQL serverless, sslmode=require 필수)
❌ townpulse.kr 아님 → townpulse.site
❌ Router → Interactor에 *Schema 직접 전달 금지 (반드시 mapper 경유)
❌ domain/에서 FastAPI, SQLAlchemy, httpx import 금지
❌ Interactor에서 Depends 사용 금지
❌ Interactor 반환값으로 Schema 또는 ORM 객체 반환 금지
❌ Result DTO에 Entity를 직접 담아 Router까지 노출 금지
❌ prescription_result_repository에서 Gemini SDK·API 키 직접 접근 금지 → **Keymaker·Smith 경유 + private 메서드 캡슐화** (별도 adapter 파일 금지) ★ v7.1
❌ TOWNPULSE_AI_PERSONA를 domain/value_objects/에 두지 말 것 → `core/matrix/grid_keymaker_secret_manager.py` 상수로 배치 ★ v7
❌ GEMINI_API_KEY·공공API·JWT 키를 adapter/repository에서 os.getenv 직접 호출 금지 → `get_keymaker()` 경유 ★ v7
❌ AsyncEngine·`get_db`·ORM Base를 matrix 외부에 중복 정의 금지 → Oracle·Neo 경유 ★ v7
❌ JWT·Depends 가드를 `shared/auth/` 등에 두지 말 것 → `core/matrix/grid_trinity_hacker_mixin.py` 경유 ★ v7
❌ 라우터 파일 1개가 여러 테이블 책임 담당 금지 → ERD 테이블 1개 = 라우터 1개 (SRP) ★ v4
❌ 오케스트레이터가 Repository를 직접 접근 금지 → 반드시 기존 UseCase Port 또는 오케스트레이터 전용 Port 경유 ★ v7
❌ VO를 특정 도메인 entity 파일 내부에 정의 금지 → domain/value_objects/ 공용 배치 (AOP) ★ v5
❌ 오케스트레이터 Interactor가 다른 오케스트레이터 Interactor를 직접 import 금지 → Provider Depends 체이닝 경유 ★ v5
❌ 공공API "5개 실연동" 가정 금지 → **실연동 8개 확정** (v8.2: 버스 data.go.kr 2건→1건) ★ v6
❌ `registered_households`를 SNAP_BUILDING에 쓰지 말 것 → **SNAP_POPULATION 소속** (SRP: 인구 도메인 값이 건물 어댑터 테이블에 끼어들면 안 됨) ★ v6
❌ `fiscal_self_reliance`를 SNAP_POPULATION(읍면동 단위)에 쓰지 말 것 → **REGION(시군구 단위) 소속** (정규화: 시군구 지표를 읍면동 테이블에 두면 동일 시군 내 모든 읍면동이 값을 중복 저장) ★ v6
❌ `birth_rate`·`daytime_population`을 SNAP_POPULATION에 쓰지 말 것 → **REGION(시군구, KOSIS #8)** — `fiscal_self_reliance`와 동일 패턴, MVP TVI 미사용 ★ v8.4
❌ SNAP_* 조인에 `emd_code`(행정동코드)를 메인 키로 쓰지 말 것 → **`REGION.legal_dong_code`(법정동코드)가 메인 조인키**, `emd_code`는 nullable 참조용(법정동:행정동 1:1 아님, 공란 흔함) ★ v6
❌ TAGO 폴백(API#7)을 별도 ingest로 두지 말 것 → **#6·#7 동일 `BusRouteInfoInqireService`** ★ v8.2
❌ 버스 API를 1회 호출로 가정하지 말 것 → **2단계 필수**(① getRouteNoList→routeId, ② getRouteInfoIem→intervaltime) ★ v6
❌ Assembler/Mapper를 Router~UseCase 사이의 별도 호출 "층"으로 그리지 말 것 → **Router·Repository 경계(톨게이트)에서만 타입 변환**, Router 함수 내부에서 호출 (구조.md §1.1) ★ v6
❌ 예외적인 ai_text_generator_port.py를 단독으로 만들지 말 것 → **prescription_result_port.py로 병합/삭제** (프랙탈 규격 정합) ★ v7
❌ `adapter/outbound/ai/`·`{domain}_gemini_adapter.py`·`{domain}_public_adapter.py` 등 **13번째 outbound 파일 생성 금지** → Gemini·공공API는 **`{table}_repository.py` 내부 private 메서드** (12파일 프랙탈 유지) ★ v8
❌ `adapter/outbound/pipeline/`·`core/matrix/grid_batch_scheduler.py`·`grid_public_data_collector.py` 생성 금지 → 배치 cron·조율·수동 트리거는 **`public_data_sync_orchestrator_*` 12파일 프랙탈 + Provider APScheduler** ★ v8.1
❌ `_memory_repository` 생성·Provider DB 분기 금지 — Repository는 NeonDB 단일 구현 ★ v7
✅ 프론트(Vercel, townpulse.site) ↔ 백엔드(**Railway**, api.townpulse.site) 연동 ★ v9.2
✅ SSE 스트리밍: 프론트가 ?token=JWT 쿼리 파라미터로 전송 → 백엔드에서 token: str = Query(...) 수신
✅ 예산 단위: DB에 만원 단위 정수 저장 (27000 = 2.7억원)
✅ village_code: 10자리 문자열 VARCHAR(10), 숫자 아닌 문자열로 처리
✅ grade_filter: Application 레이어(Interactor)에서 처리, Repository SQL에서 처리하지 않음
✅ Repository는 NeonDB 단일 구현 — _memory_repository 미사용 ★ v7
✅ API 키·Gemini 클라이언트·`.env.local` 로드는 `core/matrix/grid_keymaker_secret_manager.py` (Keymaker) 단일 진입점 ★ v7
✅ NeonDB AsyncEngine·`get_db`는 Oracle, ORM `DeclarativeBase`는 Neo — `core/matrix/` 단일 진입점 ★ v7
✅ JWT·FastAPI Depends·SSE token 검증은 Trinity — `core/matrix/grid_trinity_hacker_mixin.py` ★ v7
✅ 라우터 18개 = ERD 테이블 18개 1:1 대응 (SRP 완전 준수) ★ v4
✅ 오케스트레이터 4개 = 총 22개 도메인 (18 ERD + 오케스트레이터 4), 프랙탈 풀세트 22×12 유지 ★ v8.1
✅ VO = AOP 횡단 관심사 → domain/value_objects/ 단독 배치, 프랙탈 구조 미적용 ★ v5
✅ report_orchestrator는 village_detail_orchestrator를 Provider Depends 체이닝으로 재사용 ★ v5
✅ public_data_sync_orchestrator는 Region·Village·SNAP×4·TVI **Output Port 7개** Depends 체이닝 — ingest 구현은 각 Repository private ★ v8.1
✅ APScheduler·register_batch_jobs는 `public_data_sync_orchestrator_provider.py` 단일 — matrix 배치 파일 없음 ★ v8.1
✅ REGION 코드체계 4종: `sigungu_code`(건축HUB) / `legal_dong_code`(★메인 조인키, 건축HUB·인구3종) / `emd_code`(nullable, 참조용) / `tago_city_code`(버스 API cityCode) ★ v6 → v8.2
✅ `snap_population_repository` — `ingest_core_from_public_api()`(#2+#3) + `ingest_migration_from_public_api()`(#4, §10-8-1) → SNAP_POPULATION 1행 ★ v9.0
✅ `snap_transport_repository.ingest_for_village()` — **BusRouteInfoInqireService 2단계 + BusSttnInfoInqireService(15098534)** , `VILLAGE.lat/lng`(vworld) 필수 ★ v8.3
✅ `region_repository.ingest_fiscal_self_reliance()`는 REGION·연 1회 cron — 월간 collect_all과 분리 ★ v8
✅ `region_repository.ingest_kosis_sigungu_demographics()` — `birth_rate`·`daytime_population` (KOSIS #8, 시군구, v1.0 ingest, MVP 미적재) ★ v8.4
✅ `snap_building_repository.ingest_from_public_api()` — `sigunguCd`+`bjdongCd[5:10]`+전 페이지 페이징 ★ v8.4
✅ `tvi_score_repository.recalculate_all()` — §9 min-max + `calculate_tvi()` · `simulate_tvi_gain()` ★ v8.5
✅ MVP TVI(0.70/0.20/0.10)에 `birth_rate`·`daytime_population` **미사용** — v1.0 시군구 보정 검토 ★ v8.4
```

---

## 목차

1. [기술 스택 및 환경](#1-기술-스택-및-환경)
2. [인프라 구성](#2-인프라-구성)
3. [22개 도메인 개요 (ERD 컬럼)](#21-22개-도메인-개요-erd-컬럼)
4. [프로젝트 구조 (전체)](#3-프로젝트-구조-전체)
5. [아키텍처 원칙 — Titanic 프랙탈](#4-아키텍처-원칙--titanic-프랙탈)
6. [v8.1 핵심 변경 — 22×12 프랙탈 + VO AOP](#5-v81-핵심-변경--22×12-프랙탈--vo-aop)
7. [레이어별 코드 패턴](#6-레이어별-코드-패턴)
8. [API 엔드포인트 (22개 도메인)](#7-api-엔드포인트-22개-도메인)
9. [데이터베이스 스키마](#8-데이터베이스-스키마)
10. [TVI 산출 공식](#9-tvi-산출-공식)
11. [공공데이터 배치 수집 (Repository + PUBLIC_DATA_SYNC_ORCHESTRATOR)](#10-공공데이터-배치-수집-repository--public_data_sync_orchestrator--v81)
12. [Gemini AI 연동](#11-gemini-ai-연동)
13. [인증 (JWT)](#12-인증-jwt)
14. [NeonDB 연결 설정](#13-neondb-연결-설정)
15. [환경변수](#14-환경변수)
16. [Docker + 배포](#15-docker--배포)
17. [Alembic 마이그레이션](#16-alembic-마이그레이션)
18. [프론트-백 연동 계약](#17-프론트-백-연동-계약)
19. [MVP 개발 체크리스트](#18-mvp-개발-체크리스트)

---

## 1. 기술 스택 및 환경

| 분류 | 기술 | 버전 | 용도 |
|---|---|---|---|
| 웹 프레임워크 | FastAPI | 0.115+ | REST API + SSE |
| 언어 | Python | 3.12+ | 백엔드 전체 |
| ORM | SQLAlchemy | 2.0+ (async) | DB 모델·쿼리 |
| DB 드라이버 | asyncpg | 최신 | NeonDB 비동기 연결 (`core/matrix/grid_oracle_database_manager.py`) ★ v7 |
| DB | NeonDB (PostgreSQL 16) | serverless | 메인 DB |
| 마이그레이션 | Alembic | 최신 | 스키마 버전 관리 |
| 유효성 검증 | Pydantic | v2 | 스키마·설정 |
| AI (처방 생성) | Google GenAI SDK + Keymaker | 최신 | `core/matrix` Gemini API 연동 ★ v7 |
| 스케줄러 | APScheduler | 최신 | 공공데이터 배치 (`public_data_sync_orchestrator_provider.py`) ★ v8.1 |
| HTTP 클라이언트 | httpx | 최신 | 공공API 호출 |
| 환경변수 | python-dotenv + Keymaker | 최신 | `.env.local` 단일 로드 (`core/matrix`) ★ v7 |
| 로깅 | structlog | 최신 | 구조화 로그 |
| 컨테이너 | Docker + Docker Compose | 최신 | 실행 환경 |

---

## 2. 인프라 구성

```
[townpulse.site — Vercel, Next.js 14]
          ↕ HTTPS REST / SSE
[api.townpulse.site — Railway, FastAPI + Docker]
          ↕ asyncpg + sslmode=require
[NeonDB — PostgreSQL serverless]

[APScheduler] → [8개 공공API] → NeonDB (데이터 수집, 월간 SNAP_* + 연간 REGION 재정자립도 분리) ★ v6
[FastAPI 처방 라우터] → [Gemini API] → SSE 스트리밍 응답

DNS:
  townpulse.site       → Vercel (프론트)
  api.townpulse.site   → Railway 커스텀 도메인 (백엔드) ★ v9.2
SSL: Nginx 리버스 프록시 + Let's Encrypt (Certbot)
```

---

## 2-1. 22개 도메인 개요 (ERD 컬럼) ★ v8.1

> **총 22개 도메인 = ERD 18테이블 1:1 (18) + 오케스트레이터 4 (ERD 18 외, 12파일 프랙탈)**  
> 각 ERD 도메인은 `{table}_entity.py` ↔ `{table}_orm.py` ↔ NeonDB 테이블 1:1. 상세 DDL은 §8 참고.

| 구분 | # | 도메인 | NeonDB 테이블 | 역할 한줄 |
|---|---|---|---|---|
| 공간/마을 | 1 | REGION | `region` | 충북 행정구역·코드체계·재정자립도 |
| 공간/마을 | 2 | VILLAGE | `village` | 마을 마스터·좌표(vworld) |
| 공공API 스냅 | 3 | SNAP_POPULATION | `snap_population` | 인구·세대·이동 스냅샷 (API#2~4) |
| 공공API 스냅 | 4 | SNAP_BUILDING | `snap_building` | 건축물대장 스냅샷 (API#1) |
| 공공API 스냅 | 5 | SNAP_TRANSPORT | `snap_transport` | 버스 노선·배차·**정류소 접근성** (API#6 + 15098534, MVP) |
| 공공API 스냅 | 6 | SNAP_STATISTICS | `snap_statistics` | KOSIS 통계 스냅샷 (API#8) |
| TVI | 7 | TVI_SCORE | `tvi_score` | 마을별 TVI 산출 결과 |
| 처방 라이브 | 8 | PRESCRIPTION_TYPE | `prescription_type` | 처방 유형 마스터 |
| 처방 라이브 | 9 | PRESCRIPTION_INDICATOR | `prescription_indicator` | 처방↔지표 매핑 |
| 처방 라이브 | 10 | PRESCRIPTION_FUND_SOURCE | `prescription_fund_source` | 처방↔기금 매핑 |
| 처방 라이브 | 11 | DISPATCH_RULE | `dispatch_rule` | 자동 처방 매칭 규칙 |
| 처방 라이브 | 12 | BUDGET_UNIT_PRICE | `budget_unit_price` | 처방별 단가 라이브러리 |
| 처방 결과 | 13 | PRESCRIPTION_RESULT | `prescription_result` | 마을 처방 생성·AI 설명 |
| 처방 결과 | 14 | BUDGET_ESTIMATE | `budget_estimate` | 처방별 예산 산출 |
| SaaS | 15 | ORGANIZATION | `organization` | 기관(지자체·센터) |
| SaaS | 16 | SUBSCRIPTION | `subscription` | 기관 구독 티어 |
| SaaS | 17 | USER | `townpulse_user` | 로그인 사용자 (ORM: `user_orm.py`) |
| SaaS | 18 | REPORT | `report` | PDF 리포트 이력 |
| 오케스트 | 19 | DASHBOARD_ORCHESTRATOR | *(없음 — 읽기 집계)* | D-02·D-03 대시보드 조합 |
| 오케스트 | 20 | VILLAGE_DETAIL_ORCHESTRATOR | *(없음 — 읽기 집계)* | D-04 마을 상세 조합 |
| 오케스트 | 21 | REPORT_ORCHESTRATOR | *(없음 — REPORT 재사용)* | D-06 리포트 데이터 조합 |
| 오케스트 | 22 | PUBLIC_DATA_SYNC_ORCHESTRATOR | `public_data_sync_job` | 배치 cron·수동 sync 이력 |

### ERD 18 — 테이블별 컬럼 주석

```sql
-- [#1] REGION  →  region_entity.py / region_orm.py
--   id                   UUID PK
--   sido                 VARCHAR(20)   -- 시/도명 (MVP: 충북)
--   sigungu              VARCHAR(50)   -- 시군구명
--   sigungu_code         VARCHAR(5)    -- 시군구코드 — 건축HUB API 호출
--   emd_name             VARCHAR(100)  -- 읍면동명
--   emd_code             VARCHAR(10)   -- 행정동코드 — nullable, 참조용 (조인키 아님)
--   legal_dong_code      VARCHAR(10)   -- ★법정동코드 — 메인 조인키, UNIQUE, SNAP/API 공통
--   tago_city_code       VARCHAR(10)   -- 버스 API cityCode (TAGO getCtyCodeList)
--   area_km2             FLOAT         -- 면적(선택)
--   fiscal_self_reliance FLOAT         -- 재정자립도 — 시군구 단위, API#5, 연1회
--   fiscal_data_year     DATE          -- 재정자립도 기준 연도
--   birth_rate           FLOAT         -- KOSIS #8, 시군구, v1.0 ingest, MVP TVI 미사용 ★ v8.4
--   daytime_population   FLOAT         -- KOSIS #8 주간인구지수, 시군구, 5년 주기 ★ v8.4
--   demographic_data_year DATE         -- birth/daytime 기준 연도 ★ v8.4

-- [#2] VILLAGE  →  village_entity.py / village_orm.py
--   id             UUID PK
--   region_id      UUID FK → region.id
--   name           VARCHAR(100)  -- 마을명
--   emd_code       VARCHAR(10)   -- 10자리 행정코드 (= API village_code 관례)
--   lat            FLOAT         -- 위도 — API#7 vworld geocode
--   lng            FLOAT         -- 경도
--   last_synced_at TIMESTAMP     -- geocode 마지막 동기화 시각

-- [#3] SNAP_POPULATION  →  snap_population_entity.py  (API#2+#3+#4)
--   id                    UUID PK
--   village_id            UUID FK → village.id
--   snapshot_date         DATE      -- 스냅샷 기준일 (월간 배치)
--   population_total      INTEGER   -- 총인구 — API#2
--   population_65plus     INTEGER   -- 65세 이상 — API#3
--   population_youth      INTEGER   -- 청년층 — API#3
--   registered_households INTEGER   -- 세대수 — API#2 (v6: BUILDING에서 이전)
--   net_youth_migration   INTEGER   -- 청년 순이동 — API#4
--   fetched_at            TIMESTAMP -- ingest 시각

-- [#4] SNAP_BUILDING  →  snap_building_entity.py  (API#1 건축HUB)
--   id                    UUID PK
--   village_id            UUID FK
--   snapshot_date         DATE
--   residential_buildings INTEGER   -- 주거용 건축물 수 (mainPurpsCdNm 화이트리스트 COUNT)
--   fetched_at            TIMESTAMP

-- [#5] SNAP_TRANSPORT  →  snap_transport_entity.py  (API#6 + 15098534, MVP)
--   id                         UUID PK
--   village_id                 UUID FK
--   snapshot_date              DATE
--   bus_route_count            INTEGER   -- 시/군(tago_city_code) getRouteNoList totalCount
--   avg_bus_interval_min       FLOAT     -- 시/군 노선 getRouteInfoIem intervaltime 평균(평일)
--   nearest_stop_distance_m    INTEGER   -- 마을↔최근접 정류장(m), 15098534 + vworld 좌표
--   bus_stops_within_1km       INTEGER   -- 1km 내 정류장 수 (§10-9: 15098534+노선카탈로그)
--   fetched_at                 TIMESTAMP

-- [#6] SNAP_STATISTICS  →  snap_statistics_entity.py  (API#8 KOSIS)
--   id            UUID PK
--   village_id    UUID FK
--   snapshot_date DATE
--   aging_ratio   FLOAT     -- 고령화율
--   youth_ratio   FLOAT     -- 청년 비율
--   pop_density   FLOAT     -- 인구밀도
--   fetched_at    TIMESTAMP

-- [#7] TVI_SCORE  →  tvi_score_entity.py  (§9 산식, SNAP 교차 read 후 write)
--   id                 UUID PK
--   village_id         UUID FK
--   calculated_at      DATE
--   tvi_score          FLOAT NOT NULL   -- 종합 TVI 0~100
--   risk_level         VARCHAR(10)      -- danger | warning | safe
--   pop_decline_score  FLOAT            -- 인구감소 부분점수 (가중 0.70)
--   vacancy_rate       FLOAT            -- 공실 추정 부분점수 (가중 0.20)
--   bus_interval_score FLOAT            -- 버스 접근성 부분점수 (가중 0.10)
--   prev_tvi_score     FLOAT            -- 직전 TVI (delta용)
--   tvi_delta          FLOAT            -- 전월 대비 변화
--   model_version      VARCHAR(50)      -- 예: weighted_sum_v1

-- [#8] PRESCRIPTION_TYPE  →  prescription_type_entity.py
--   id               UUID PK
--   code             VARCHAR(50) UNIQUE  -- 처방 코드 (프론트·룰 참조)
--   name             VARCHAR(100)        -- 표시명
--   category         VARCHAR(50)         -- 분류
--   rollout_timeline VARCHAR(20)         -- urgent | medium | long
--   is_active        BOOLEAN             -- 활성 여부

-- [#9] PRESCRIPTION_INDICATOR  →  prescription_indicator_entity.py
--   id                   UUID PK
--   prescription_type_id UUID FK → prescription_type.id
--   indicator_code       VARCHAR(50)   -- TVI/지표 코드
--   effect_direction     VARCHAR(20)   -- positive | negative

-- [#10] PRESCRIPTION_FUND_SOURCE  →  prescription_fund_source_entity.py
--   id                   UUID PK
--   prescription_type_id UUID FK
--   fund_name            VARCHAR(200)  -- 기금명
--   fund_org             VARCHAR(100)  -- 주관 기관
--   is_eligible          BOOLEAN       -- 해당 처방 적격 여부

-- [#11] DISPATCH_RULE  →  dispatch_rule_entity.py
--   id                   UUID PK
--   prescription_type_id UUID FK
--   trigger_indicator    VARCHAR(50)   -- 트리거 지표
--   operator             VARCHAR(10)   -- gt | lt | gte | lte
--   threshold_value      FLOAT         -- 임계값
--   priority_rank        INTEGER       -- 1·2·3 순위

-- [#12] BUDGET_UNIT_PRICE  →  budget_unit_price_entity.py
--   id                   UUID PK
--   prescription_type_id UUID FK
--   unit                 VARCHAR(20)   -- 단위 (명·km 등)
--   price_min            BIGINT        -- 만원 단위 하한
--   price_max            BIGINT        -- 만원 단위 상한
--   reference_source     VARCHAR(300)  -- 산출 근거
--   effective_from       DATE          -- 적용 시작일

-- [#13] PRESCRIPTION_RESULT  →  prescription_result_entity.py
--   id                   UUID PK
--   village_id           UUID FK
--   tvi_score_id         UUID FK → tvi_score.id
--   prescription_type_id UUID FK
--   priority_rank        INTEGER       -- 1순위·2순위·3순위
--   tvi_gain_min         FLOAT         -- 예상 TVI 개선 하한
--   tvi_gain_max         FLOAT         -- 예상 TVI 개선 상한
--   fund_applicable      BOOLEAN       -- 기금 적용 가능 여부
--   ai_description       TEXT          -- Gemini 생성 설명 (SSE 저장)
--   generated_at         TIMESTAMP

-- [#14] BUDGET_ESTIMATE  →  budget_estimate_entity.py
--   id                     UUID PK
--   prescription_result_id UUID FK
--   budget_unit_price_id   UUID FK
--   quantity               INTEGER     -- 수량
--   budget_min             BIGINT      -- 만원 단위
--   budget_max             BIGINT
--   calculation_note       TEXT

-- [#15] ORGANIZATION  →  organization_entity.py
--   id          UUID PK
--   name        VARCHAR(200)  -- 기관명
--   org_type    VARCHAR(50)   -- 지자체·센터 등
--   region_code VARCHAR(10)   -- 담당 행정구역
--   created_at  TIMESTAMP

-- [#16] SUBSCRIPTION  →  subscription_entity.py
--   id              UUID PK
--   organization_id UUID FK
--   tier            VARCHAR(20)   -- basic | standard | premium
--   started_at      DATE
--   expires_at      DATE
--   is_active       BOOLEAN
--   monthly_fee     BIGINT        -- 만원 단위

-- [#17] USER  →  user_entity.py / user_orm.py  (DB 테이블명: townpulse_user)
--   id              UUID PK
--   organization_id UUID FK
--   name            VARCHAR(100)
--   email           VARCHAR(200) UNIQUE
--   password_hash   VARCHAR(255) NOT NULL  -- bcrypt — §12-1c ★ v9.1
--   role            VARCHAR(20)   -- viewer | admin (MVP QA: admin 1건)
--   last_login_at   TIMESTAMP

-- [#18] REPORT  →  report_entity.py
--   id           UUID PK
--   user_id      UUID FK → townpulse_user.id
--   village_id   UUID FK
--   tvi_score_id UUID FK
--   title        VARCHAR(300)
--   format       VARCHAR(20)   -- pdf 등
--   file_url     VARCHAR(1000) -- S3/스토리지 URL
--   generated_at TIMESTAMP
```

### 오케스트레이터 4 — ERD 18 외 (12파일 프랙탈)

> 화면·배치 **조율 전용**. Entity/ORM은 집계 read model 또는 보조 이력 테이블만 둔다. 비즈니스 write는 기존 ERD 도메인 Repository가 담당.

```sql
-- [#19] DASHBOARD_ORCHESTRATOR
--   NeonDB: 전용 테이블 없음 (dashboard_orchestrator_orm.py = 집계 뷰/쿼리 read model)
--   Entity: DashboardSummaryReadModel 등 — TVI·VILLAGE·SNAP 조합 결과 DTO용
--   조합: TVI + VILLAGE + SNAP_BUILDING + SNAP_TRANSPORT UseCase 4개

-- [#20] VILLAGE_DETAIL_ORCHESTRATOR
--   NeonDB: 전용 테이블 없음 (복합 조회 뷰)
--   Entity: VillageDetailReadModel — SNAP×4 + TVI + PRESCRIPTION_RESULT 상위2
--   조합: UseCase 7개 asyncio.gather

-- [#21] REPORT_ORCHESTRATOR
--   NeonDB: REPORT 테이블 재사용 (리포트 이력 write는 report_repository)
--   Entity: ReportOrchestratorReadModel — village_detail 재사용 + 예산
--   조합: village_detail_orchestrator + BUDGET_ESTIMATE + ORGANIZATION

-- [#22] PUBLIC_DATA_SYNC_ORCHESTRATOR  →  public_data_sync_orchestrator_orm.py
--   id              UUID PK
--   job_type        VARCHAR(30)   -- MONTHLY_SNAP | FISCAL_YEARLY (sync_job_type_vo)
--   status          VARCHAR(20)   -- PENDING | RUNNING | COMPLETED | FAILED
--   started_at      TIMESTAMP
--   finished_at     TIMESTAMP     -- nullable
--   error_message   TEXT          -- FAILED 시
--   processed_count INTEGER       -- 처리 건수 (법정동·마을 루프)
--   created_at      TIMESTAMP DEFAULT NOW()
--   ingest 실행: 타 도메인 Output Port 7개 — §10
```

> **프랙탈 파일 접두:** ERD 도메인은 테이블명 snake_case (`region_*`, `snap_population_*`). 오케스트레이터는 `{name}_orchestrator_*` (`dashboard_orchestrator_router.py` 등). §3 트리·§5 매핑표와 1:1 대응.

---

## 3. 프로젝트 구조 (전체)

```
townpulse-api/
├── main.py
├── core/                                    # 시스템 전역 — apps와 동급 ★ v7
│   └── matrix/
│       ├── __init__.py
│       ├── grid_keymaker_secret_manager.py  # Keymaker — .env.local, get_secret(), Gemini Client, AI persona ★ v7
│       ├── grid_oracle_database_manager.py  # Oracle — NeonDB AsyncEngine, get_db, dispose_engine ★ v7
│       ├── grid_neo_theone_base.py          # Neo — DeclarativeBase (ORM metadata 단일 원천) ★ v7
│       ├── grid_morpheus_base_orchestrator.py # Morpheus — 오케스트레이터 Interactor 공통 베이스 ★ v7
│       ├── grid_trinity_hacker_mixin.py     # Trinity — JWT 발급·검증, FastAPI Depends (구 shared/auth) ★ v7
│       └── grid_smith_agent_scaler.py       # Smith — Gemini 모델 폴백·429 재시도 ★ v7
├── apps/
│   └── townpulse/
│       ├── domain/
│       │   ├── entities/
│       │   │   ├── region_entity.py
│       │   │   ├── village_entity.py
│       │   │   ├── snap_population_entity.py
│       │   │   ├── snap_building_entity.py
│       │   │   ├── snap_transport_entity.py
│       │   │   ├── snap_statistics_entity.py
│       │   │   ├── tvi_score_entity.py
│       │   │   ├── prescription_type_entity.py
│       │   │   ├── prescription_indicator_entity.py
│       │   │   ├── prescription_fund_source_entity.py
│       │   │   ├── dispatch_rule_entity.py
│       │   │   ├── budget_unit_price_entity.py
│       │   │   ├── prescription_result_entity.py
│       │   │   ├── budget_estimate_entity.py
│       │   │   ├── organization_entity.py
│       │   │   ├── subscription_entity.py
│       │   │   ├── user_entity.py
│       │   │   ├── report_entity.py
│       │   │   ├── dashboard_orchestrator_entity.py          # ★ v7 추가
│       │   │   ├── village_detail_orchestrator_entity.py      # ★ v7 추가
│       │   │   ├── report_orchestrator_entity.py             # ★ v7 추가
│       │   │   └── public_data_sync_orchestrator_entity.py   # ★ v8.1: 동기화 job 이력
│       │   └── value_objects/               # AOP — 프랙탈 구조 미적용, 횡단 공용 ★ v5
│       │       ├── village_code_vo.py
│       │       ├── tvi_score_vo.py
│       │       ├── tvi_grade_vo.py
│       │       ├── prescription_priority_vo.py
│       │       ├── village_snapshot_vo.py   # 오케스트레이터용 SNAP 4개 복합 VO
│       │       ├── sync_job_type_vo.py      # ★ v8.1: MONTHLY_SNAP | FISCAL_YEARLY
│       │       ├── sync_job_status_vo.py    # ★ v8.1: PENDING | RUNNING | COMPLETED | FAILED
│       │       ├── residential_purpose_vo.py  # ★ v8.10: mainPurpsCdNm 화이트리스트·is_residential()
│       │       └── sido_code_vo.py            # ★ v9.0: API#4 시/도 17개 스윕 상수·sido_admm_cd()
│       │
│       ├── app/
│       │   ├── ports/
│       │   │   ├── input/
│       │   │   │   ├── region_use_case.py
│       │   │   │   ├── village_use_case.py
│       │   │   │   ├── snap_population_use_case.py
│       │   │   │   ├── snap_building_use_case.py
│       │   │   │   ├── snap_transport_use_case.py
│       │   │   │   ├── snap_statistics_use_case.py
│       │   │   │   ├── tvi_score_use_case.py
│       │   │   │   ├── prescription_type_use_case.py
│       │   │   │   ├── prescription_indicator_use_case.py
│       │   │   │   ├── prescription_fund_source_use_case.py
│       │   │   │   ├── dispatch_rule_use_case.py
│       │   │   │   ├── budget_unit_price_use_case.py
│       │   │   │   ├── prescription_result_use_case.py
│       │   │   │   ├── budget_estimate_use_case.py
│       │   │   │   ├── organization_use_case.py
│       │   │   │   ├── subscription_use_case.py
│       │   │   │   ├── user_use_case.py
│       │   │   │   ├── report_use_case.py
│       │   │   │   ├── dashboard_orchestrator_use_case.py    # ★ v5
│       │   │   │   ├── village_detail_orchestrator_use_case.py  # ★ v5
│       │   │   │   ├── report_orchestrator_use_case.py       # ★ v5
│       │   │   │   └── public_data_sync_orchestrator_use_case.py  # ★ v8.1
│       │   │   └── output/
│       │   │       ├── region_port.py
│       │   │       ├── village_port.py
│       │   │       ├── snap_population_port.py
│       │   │       ├── snap_building_port.py
│       │   │       ├── snap_transport_port.py
│       │   │       ├── snap_statistics_port.py
│       │   │       ├── tvi_score_port.py
│       │   │       ├── prescription_type_port.py
│       │   │       ├── prescription_indicator_port.py
│       │   │       ├── prescription_fund_source_port.py
│       │   │       ├── dispatch_rule_port.py
│       │   │       ├── budget_unit_price_port.py
│       │   │       ├── prescription_result_port.py            # ★ v7 AI 텍스트 생성 포트(IAiTextGenerator) 병합
│       │   │       ├── budget_estimate_port.py
│       │   │       ├── organization_port.py
│       │   │       ├── subscription_port.py
│       │   │       ├── user_port.py
│       │   │       ├── report_port.py
│       │   │       ├── dashboard_orchestrator_port.py         # ★ v7 추가
│       │   │       ├── village_detail_orchestrator_port.py     # ★ v7 추가
│       │   │       ├── report_orchestrator_port.py            # ★ v7 추가
│       │   │       └── public_data_sync_orchestrator_port.py  # ★ v8.1: job 이력
│       │   ├── use_cases/
│       │   │   ├── region_interactor.py
│       │   │   ├── village_interactor.py
│       │   │   ├── snap_population_interactor.py
│       │   │   ├── snap_building_interactor.py
│       │   │   ├── snap_transport_interactor.py
│       │   │   ├── snap_statistics_interactor.py
│       │   │   ├── tvi_score_interactor.py
│       │   │   ├── prescription_type_interactor.py
│       │   │   ├── prescription_indicator_interactor.py
│       │   │   ├── prescription_fund_source_interactor.py
│       │   │   ├── dispatch_rule_interactor.py
│       │   │   ├── budget_unit_price_interactor.py
│       │   │   ├── prescription_result_interactor.py
│       │   │   ├── budget_estimate_interactor.py
│       │   │   ├── organization_interactor.py
│       │   │   ├── subscription_interactor.py
│       │   │   ├── user_interactor.py
│       │   │   ├── report_interactor.py
│       │   │   ├── dashboard_orchestrator_interactor.py       # ★ v7 접미사 통일
│       │   │   ├── village_detail_orchestrator_interactor.py  # ★ v7 접미사 통일
│       │   │   ├── report_orchestrator_interactor.py          # ★ v7 접미사 통일
│       │   │   └── public_data_sync_orchestrator_interactor.py  # ★ v8.1: 배치 조율
│       │   └── dtos/
│       │       ├── region_dto.py
│       │       ├── village_dto.py
│       │       ├── snap_population_dto.py
│       │       ├── snap_building_dto.py
│       │       ├── snap_transport_dto.py
│       │       ├── snap_statistics_dto.py
│       │       ├── tvi_score_dto.py
│       │       ├── prescription_type_dto.py
│       │       ├── prescription_indicator_dto.py
│       │       ├── prescription_fund_source_dto.py
│       │       ├── dispatch_rule_dto.py
│       │       ├── budget_unit_price_dto.py
│       │       ├── prescription_result_dto.py
│       │       ├── budget_estimate_dto.py
│       │       ├── organization_dto.py
│       │       ├── subscription_dto.py
│       │       ├── user_dto.py
│       │       ├── report_dto.py
│       │       ├── dashboard_orchestrator_dto.py      # ★ v5
│       │       ├── village_detail_orchestrator_dto.py # ★ v5
│       │       ├── report_orchestrator_dto.py         # ★ v5
│       │       └── public_data_sync_orchestrator_dto.py # ★ v8.1
│       │
│       ├── adapter/
│       │   ├── inbound/
│       │   │   ├── api/
│       │   │   │   ├── __init__.py            # townpulse_router 집계 (22개 등록) ★ v8.1
│       │   │   │   ├── v1/
│       │   │   │   │   ├── region_router.py
│       │   │   │   │   ├── village_router.py
│       │   │   │   │   ├── snap_population_router.py
│       │   │   │   │   ├── snap_building_router.py
│       │   │   │   │   ├── snap_transport_router.py
│       │   │   │   │   ├── snap_statistics_router.py
│       │   │   │   │   ├── tvi_score_router.py
│       │   │   │   │   ├── prescription_type_router.py
│       │   │   │   │   ├── prescription_indicator_router.py
│       │   │   │   │   ├── prescription_fund_source_router.py
│       │   │   │   │   ├── dispatch_rule_router.py
│       │   │   │   │   ├── budget_unit_price_router.py
│       │   │   │   │   ├── prescription_result_router.py
│       │   │   │   │   ├── budget_estimate_router.py
│       │   │   │   │   ├── organization_router.py
│       │   │   │   │   ├── subscription_router.py
│       │   │   │   │   ├── user_router.py
│       │   │   │   │   ├── report_router.py
│       │   │   │   │   ├── dashboard_orchestrator_router.py      # ★ v5: D-02 + 지도 요약
│       │   │   │   │   ├── village_detail_orchestrator_router.py # ★ v5: D-04 + M-03
│       │   │   │   │   ├── report_orchestrator_router.py         # ★ v5: D-06 + M-05
│       │   │   │   │   └── public_data_sync_orchestrator_router.py  # ★ v8.1: admin sync
│       │   │   │   └── schemas/
│       │   │   │       ├── region_schema.py
│       │   │   │       ├── village_schema.py
│       │   │   │       ├── snap_population_schema.py
│       │   │   │       ├── snap_building_schema.py
│       │   │   │       ├── snap_transport_schema.py
│       │   │   │       ├── snap_statistics_schema.py
│       │   │   │       ├── tvi_score_schema.py
│       │   │   │       ├── prescription_type_schema.py
│       │   │   │       ├── prescription_indicator_schema.py
│       │   │   │       ├── prescription_fund_source_schema.py
│       │   │   │       ├── dispatch_rule_schema.py
│       │   │   │       ├── budget_unit_price_schema.py
│       │   │   │       ├── prescription_result_schema.py
│       │   │   │       ├── budget_estimate_schema.py
│       │   │   │       ├── organization_schema.py
│       │   │   │       ├── subscription_schema.py
│       │   │   │       ├── user_schema.py
│       │   │   │       ├── report_schema.py
│       │   │   │       ├── dashboard_orchestrator_schema.py      # ★ v5
│       │   │   │       ├── village_detail_orchestrator_schema.py # ★ v5
│       │   │   │       ├── report_orchestrator_schema.py         # ★ v5
│       │   │   │       └── public_data_sync_orchestrator_schema.py  # ★ v8.1
│       │   │   └── mappers/
│       │   │       ├── region_mapper.py
│       │   │       ├── village_mapper.py
│       │   │       ├── snap_population_mapper.py
│       │   │       ├── snap_building_mapper.py
│       │   │       ├── snap_transport_mapper.py
│       │   │       ├── snap_statistics_mapper.py
│       │   │       ├── tvi_score_mapper.py
│       │   │       ├── prescription_type_mapper.py
│       │   │       ├── prescription_indicator_mapper.py
│       │   │       ├── prescription_fund_source_mapper.py
│       │   │       ├── dispatch_rule_mapper.py
│       │   │       ├── budget_unit_price_mapper.py
│       │   │       ├── prescription_result_mapper.py
│       │   │       ├── budget_estimate_mapper.py
│       │   │       ├── organization_mapper.py
│       │   │       ├── subscription_mapper.py
│       │   │       ├── user_mapper.py
│       │   │       ├── report_mapper.py
│       │   │       ├── dashboard_orchestrator_mapper.py      # ★ v5
│       │   │       ├── village_detail_orchestrator_mapper.py # ★ v5
│       │   │       ├── report_orchestrator_mapper.py         # ★ v5
│       │   │       └── public_data_sync_orchestrator_mapper.py  # ★ v8.1
│       │   └── outbound/
│       │       ├── orm/
│       │       │   ├── region_orm.py
│       │       │   ├── village_orm.py
│       │       │   ├── snap_population_orm.py
│       │       │   ├── snap_building_orm.py
│       │       │   ├── snap_transport_orm.py
│       │       │   ├── snap_statistics_orm.py
│       │       │   ├── tvi_score_orm.py
│       │       │   ├── prescription_type_orm.py
│       │       │   ├── prescription_indicator_orm.py
│       │       │   ├── prescription_fund_source_orm.py
│       │       │   ├── dispatch_rule_orm.py
│       │       │   ├── budget_unit_price_orm.py
│       │       │   ├── prescription_result_orm.py
│       │       │   ├── budget_estimate_orm.py
│       │       │   ├── organization_orm.py
│       │       │   ├── subscription_orm.py
│       │       │   ├── user_orm.py
│       │       │   ├── report_orm.py
│       │       │   ├── dashboard_orchestrator_orm.py          # ★ v5: 집계 뷰 전용 (읽기)
│       │       │   ├── village_detail_orchestrator_orm.py     # ★ v5: 복합 조회 뷰 (읽기)
│       │       │   ├── report_orchestrator_orm.py             # ★ v5: 리포트 이력 저장 포함
│       │       │   └── public_data_sync_orchestrator_orm.py   # ★ v8.1: public_data_sync_job
│       │       ├── repositories/
│       │       │   ├── region_repository.py                       # ★ v8 ingest_fiscal_self_reliance (API#5, 연1회)
│       │       │   ├── village_repository.py                      # ★ v8 update_geocode_from_vworld (API#8)
│       │       │   ├── snap_population_repository.py              # ★ v9.0 ingest_core + ingest_migration (API#2~4)
│       │       │   ├── snap_building_repository.py                # ★ v8 ingest_from_public_api (API#1)
│       │       │   ├── snap_transport_repository.py               # ★ v8.3 ingest_for_village (#6 + 15098534)
│       │       │   ├── snap_statistics_repository.py              # ★ v8 ingest_from_public_api (API#8)
│       │       │   ├── tvi_score_repository.py                    # ★ v8 recalculate_all (§9)
│       │       │   ├── prescription_type_repository.py
│       │       │   ├── prescription_indicator_repository.py
│       │       │   ├── prescription_fund_source_repository.py
│       │       │   ├── dispatch_rule_repository.py
│       │       │   ├── budget_unit_price_repository.py
│       │       │   ├── prescription_result_repository.py          # ★ v7.1 NeonDB + Gemini(SSE) — 구 outbound/ai/ 흡수
│       │       │   ├── budget_estimate_repository.py
│       │       │   ├── organization_repository.py
│       │       │   ├── subscription_repository.py
│       │       │   ├── user_repository.py
│       │       │   ├── report_repository.py
│       │       │   ├── dashboard_orchestrator_repository.py          # ★ v5
│       │       │   ├── village_detail_orchestrator_repository.py     # ★ v5
│       │       │   ├── report_orchestrator_repository.py             # ★ v5
│       │       │   └── public_data_sync_orchestrator_repository.py   # ★ v8.1
│       │       │   └── db_init.py
│       │       ├── orm_mappers/
│       │       │   ├── region_orm_mapper.py
│       │       │   ├── village_orm_mapper.py
│       │       │   ├── snap_population_orm_mapper.py
│       │       │   ├── snap_building_orm_mapper.py
│       │       │   ├── snap_transport_orm_mapper.py
│       │       │   ├── snap_statistics_orm_mapper.py
│       │       │   ├── tvi_score_orm_mapper.py
│       │       │   ├── prescription_type_orm_mapper.py
│       │       │   ├── prescription_indicator_orm_mapper.py
│       │       │   ├── prescription_fund_source_orm_mapper.py
│       │       │   ├── dispatch_rule_orm_mapper.py
│       │       │   ├── budget_unit_price_orm_mapper.py
│       │       │   ├── prescription_result_orm_mapper.py
│       │       │   ├── budget_estimate_orm_mapper.py
│       │       │   ├── organization_orm_mapper.py
│       │       │   ├── subscription_orm_mapper.py
│       │       │   ├── user_orm_mapper.py
│       │       │   ├── report_orm_mapper.py
│       │       │   ├── dashboard_orchestrator_orm_mapper.py      # ★ v5
│       │       │   ├── village_detail_orchestrator_orm_mapper.py # ★ v5
│       │       │   ├── report_orchestrator_orm_mapper.py         # ★ v5
│       │       │   └── public_data_sync_orchestrator_orm_mapper.py  # ★ v8.1
│       │
│       └── dependencies/
│           ├── region_provider.py
│           ├── village_provider.py
│           ├── snap_population_provider.py
│           ├── snap_building_provider.py
│           ├── snap_transport_provider.py
│           ├── snap_statistics_provider.py
│           ├── tvi_score_provider.py
│           ├── prescription_type_provider.py
│           ├── prescription_indicator_provider.py
│           ├── prescription_fund_source_provider.py
│           ├── dispatch_rule_provider.py
│           ├── budget_unit_price_provider.py
│           ├── prescription_result_provider.py
│           ├── budget_estimate_provider.py
│           ├── organization_provider.py
│           ├── subscription_provider.py
│           ├── user_provider.py
│           ├── report_provider.py
│           ├── dashboard_orchestrator_provider.py          # ★ v5: UseCase 4개 주입
│           ├── village_detail_orchestrator_provider.py     # ★ v5: UseCase 7개 주입
│           ├── report_orchestrator_provider.py             # ★ v5: village_detail_orch + 3개 주입
│           └── public_data_sync_orchestrator_provider.py   # ★ v8.1: Port 7개 + APScheduler
│
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.local
├── .env.production
├── alembic.ini
├── pyproject.toml
└── requirements.txt
```

### 3-1. `core/matrix/` 파일 역할 (구 `shared/` 흡수) ★ v8.1

| 파일 | 별칭 | 책임 | 구 대응 |
|---|---|---|---|
| `grid_keymaker_secret_manager.py` | Keymaker | `.env.local` 로드, `get_secret()`, Gemini Client, `TOWNPULSE_PRESCRIPTION_PERSONA` | `config/settings.py`, `ai/townpulse_ai_persona.py` |
| `grid_oracle_database_manager.py` | Oracle | AsyncEngine, `get_db`, `dispose_engine`, `create_all_tables` | (신규) |
| `grid_neo_theone_base.py` | Neo | `DeclarativeBase` — Alembic·ORM metadata | Oracle Base 분리 |
| `grid_morpheus_base_orchestrator.py` | Morpheus | 오케스트레이터 4종 Interactor 공통 베이스 (`asyncio.gather` + 순차 ingest) | (신규) |
| `grid_trinity_hacker_mixin.py` | Trinity | JWT 발급·검증, `get_current_user`, SSE `?token=` Depends | `shared/auth/` |
| `grid_smith_agent_scaler.py` | Smith | Gemini 429 할당량 시 모델 폴백·재시도 | Keymaker 폴백 분리 |
> `shared/`·`adapter/outbound/pipeline/`·`grid_batch_scheduler.py`·`grid_public_data_collector.py` **삭제** — matrix **7파일** + **22×12** 프랙탈. 배치 조율·APScheduler는 `public_data_sync_orchestrator_provider.py`. 공공API·TVI·Gemini는 `{table}_repository.py` private.

## 4. 아키텍처 원칙 — Titanic 프랙탈

### 4-1. v8.1 핵심 원칙 — 22×12 프랙탈 + VO AOP + Matrix 7파일 ★ v8.1

```
[18개 ERD 도메인]
ERD 테이블  →  Router  →  Schema  →  inbound Mapper  →  UseCase Port
     1개    →   1개    →   1개   →       1개        →      1개
     1개    →  Interactor  →  Output Port  →  Repository  →  ORM
     1개    →    1개      →     1개       →     1개      →  1개

[4개 오케스트레이터 도메인] ★ v8.1
화면/배치   →  Router  →  Schema  →  inbound Mapper  →  UseCase Port
     1개    →   1개    →   1개   →       1개        →      1개
     1개    →  Orchestrator Interactor  →  Output Port  →  Repository  →  ORM
     1개    →      1개                  →      1개      →     1개      →  1개
     dashboard / village_detail / report: 기존 UseCase Port Depends 체이닝
     public_data_sync: 타 도메인 Output Port 7개 Depends + 자체 sync 이력 Port

[VO — AOP 횡단 관심사] ★ v5 + v8.1
domain/value_objects/ — 프랙탈 구조 미적용
모든 Interactor(22개)가 공용으로 import (+ sync_job_type_vo, sync_job_status_vo)

[Matrix — 횡단 인프라만] ★ v8.1
core/matrix/ — 7파일, 프랙탈 미적용
Keymaker·Oracle·Neo·Morpheus·Trinity·Smith
공공API fetch·TVI 산식·Gemini·배치 조율·APScheduler는 Repository private / orchestrator Provider
```

### 4-2. 레이어 구조 (표준 호출 흐름)

```
방향 ① 외부 입력 (위 → 아래)
  HTTP Request
  → Router       (adapter/inbound/api/v1/{table}_router.py)  ★ v4: 테이블 1:1
  → Schema 검증  (adapter/inbound/api/schemas/{table}_schema.py)
  → inbound mapper : *Schema → QueryDTO
                     (adapter/inbound/mappers/{table}_mapper.py)
  → UseCase port (app/ports/input/{table}_use_case.py)
  → Interactor   (app/use_cases/{table}_interactor.py)
    ├─ 도메인 필터 처리 (grade_filter 등)
  → Output port  (app/ports/output/{table}_port.py)
  → outbound mapper : Entity → ORM
  → Repository   (adapter/outbound/repositories/{table}_repository.py)
  → NeonDB

방향 ② DB 조회 (아래 → 위)
  NeonDB
  → Repository
  → orm_mapper : ORM → Entity
  → Interactor  ← Entity 필드 → DTO 평탄화 후 Result DTO 반환
  → inbound mapper : ResponseDTO → *Schema
  → Router
  → HTTP Response

방향 ③ AI 호출 (PRESCRIPTION_RESULT 12파일 프랙탈 — Repository 내부) ★ v7.1
  PrescriptionResultInteractor
  → PrescriptionResultPort (app/ports/output/prescription_result_port.py)
  → PrescriptionResultRepository.stream_ai_description()  # 같은 파일 내부 private Gemini 호출
      → Keymaker (core/matrix/grid_keymaker_secret_manager.py) — Gemini Client·모델 ID·persona
      → Smith (core/matrix/grid_smith_agent_scaler.py) — 429 시 모델 폴백
      → Google Gemini API

방향 ④ 배치 적재 (cron + admin HTTP — PUBLIC_DATA_SYNC_ORCHESTRATOR) ★ v8.1
  APScheduler (Provider) → public_data_sync_orchestrator_interactor.collect_all() / ingest_fiscal_all()
      → RegionPort·VillagePort·Snap*Port·TviScorePort (Output Port 경유)
      → 각 Repository.ingest_*()·recalculate_all() private 구현
  POST /admin/sync/trigger — Router → Interactor (동일 경로)
  ※ matrix collector·Repository 직접 호출 금지
```

### 4-3. 레이어별 책임

| 레이어 | 경로 | 책임 | 금지 |
|--------|------|------|------|
| **Domain Entity** | `domain/entities/` | Entity (22개 도메인) | FastAPI, SQLAlchemy, httpx |
| **Domain VO (AOP)** | `domain/value_objects/` | 횡단 도메인 규칙 — 프랙탈 구조 미적용 ★ v5 | 특정 도메인 종속, AI 프롬프트 상수 |
| **Application** | `app/` | UseCase port, Interactor(22개), DTO | `Depends`, ORM 직접 접근, Gemini SDK·API 키 직접 호출 |
| **Core (Matrix)** | `core/matrix/` | Keymaker, Oracle, Neo, Morpheus, Trinity, Smith (7파일) ★ v8.1 | 도메인 로직, HTTP, API 파싱, 배치 조율 |
| **Inbound adapter** | `adapter/inbound/` | Router, Schema, inbound mapper (22개) | SQL, 비즈니스 규칙 |
| **Outbound adapter** | `adapter/outbound/` | Repository(NeonDB + ingest + Gemini), ORM | `HTTPException` raise |
| **Composition root** | `dependencies/` | DI wiring (오케스트레이터는 UseCase 다중 주입) | 비즈니스 로직 |

### 4-4. 프랙탈 네이밍 규칙

```
{table_name}_{layer_suffix}.py
```

| 레이어 | 접미 | 예시 (REGION) | 예시 (PRESCRIPTION_RESULT) |
|---|---|---|---|
| Router | `_router` | `region_router.py` | `prescription_result_router.py` |
| Schema | `_schema` | `region_schema.py` | `prescription_result_schema.py` |
| Inbound Mapper | `_mapper` | `region_mapper.py` | `prescription_result_mapper.py` |
| Input Port | `_use_case` | `region_use_case.py` | `prescription_result_use_case.py` |
| Output Port | `_port` | `region_port.py` | `prescription_result_port.py` |
| Interactor | `_interactor` | `region_interactor.py` | `prescription_result_interactor.py` |
| DTO | `_dto` | `region_dto.py` | `prescription_result_dto.py` |
| ORM | `_orm` | `region_orm.py` | `prescription_result_orm.py` |
| ORM Mapper | `_orm_mapper` | `region_orm_mapper.py` | `prescription_result_orm_mapper.py` |
| Repository | `_repository` | `region_repository.py` | `prescription_result_repository.py` |
| Provider | `_provider` | `region_provider.py` | `prescription_result_provider.py` |
| Entity | `_entity` | `region_entity.py` | `prescription_result_entity.py` |

> **Repository outbound 통합 규칙 ★ v8:** AI·공공API·TVI는 **`{table}_repository.py` private**만. `ai/`·`pipeline/`·`*_adapter.py` 금지. **22×12 — 13번째 outbound 파일 금지.** 배치 조율은 `public_data_sync_orchestrator_interactor`.

### 4-6. SRP — Repository outbound 통합 ★ v8.1

SRP = **변경 원인 1개 = 모듈 1개** (기술 SQL/httpx 분리 아님).

| 레이어 | SRP 단위 |
|---|---|
| **Interactor** | HTTP 유스케이스 = ERD 테이블 1개 |
| **Repository** | 그 aggregate outbound 전부 (NeonDB + 해당 공공API + PRESCRIPTION_RESULT Gemini) |
| **PUBLIC_DATA_SYNC_ORCHESTRATOR** | 배치·수동 sync **조율만** (Port 경유, API 파싱·TVI 산식 금지) |
| **Matrix** | 횡단 인프라만 (Keymaker·Oracle·Neo·Morpheus·Trinity·Smith) |

배치 `ingest_*()`는 Repository·Output Port public, sync orchestrator Interactor가 Port 경유 호출 (§10).

### 4-5. 경계 톨게이트 원칙 — `구조.md`(siliconvalley 하네스) 정합 ★ v6

> siliconvalley 형제 앱 하네스 §1.1: *"안쪽 통로(Router~Repository 인터페이스 구간)는 DTO/Entity 전용이다. Assembler·Mapper는 체인의 한 '층'이 아니다 — Router·Repository 경계(톨게이트)에서만 타입을 갈아입힌다."*

TownPulse는 titanic 관례(`use_cases/`, `mappers/`)를 그대로 따르되, **mapper의 위치적 의미**는 siliconvalley 하네스 원칙과 동일하게 해석한다.

**잘못된 그림 — mapper를 별도 레이어로 그리거나 호출**
```
Router → Mapper → UseCase → Interactor → Port → Repository → Mapper → ORM   ❌
```
이렇게 그리면 Mapper가 마치 Router·Interactor와 동급의 독립 레이어처럼 보이지만, 실제로는 **Router 함수 본문 안에서** Schema→DTO 변환을 호출하고, 그 결과 DTO를 UseCase에 넘기는 것이다. Mapper 파일이 따로 존재하는 것과, 그것이 호출 체인의 별도 "단계"인 것은 다른 이야기다.

**올바른 그림 — mapper는 Router·Repository 내부에서 호출되는 경계 변환**
```
[Router 함수 내부]
  query = SomeMapper.to_query(schema)        # 경계 변환 — Router가 직접 호출
  dto = await use_case.method(query)          # 안쪽은 DTO만 통과
  return SomeMapper.to_response_schema(dto)   # 경계 변환 — Router가 직접 호출

[Repository 메서드 내부]
  orm_row = await session.execute(...)
  entity = SomeOrmMapper.to_entity(orm_row)   # 경계 변환 — Repository가 직접 호출
  return entity
```

| 경계 | 변환 담당 | 호출 주체 | 안쪽에서 쓰는 타입 |
|------|-----------|-----------|---------------------|
| HTTP 진입/응답 | inbound mapper (`adapter/inbound/mappers/{table}_mapper.py`) | **Router가 직접 호출** | DTO |
| DB 저장/조회 | orm_mapper (`adapter/outbound/orm_mappers/{table}_orm_mapper.py`) | **Repository가 직접 호출** | Entity/DTO |

> **요약:** UseCase~Repository Port 구간(안쪽 통로)에 Schema나 ORM이 한 줄도 들어오면 안 된다 — 이건 v3부터 유지된 원칙이다. v6에서 새로 명문화한 것은 "mapper가 별도 호출 레이어가 아니라 Router/Repository의 내부 구현 디테일"이라는 점뿐이다. 22개 도메인의 기존 코드 패턴(§6)은 이미 이 원칙을 따르고 있으므로 **코드 변경은 불필요**, 문서·다이어그램 표기만 톨게이트 관점으로 명확화한다.

---

## 5. v8.1 핵심 변경 — 22×12 프랙탈 + VO AOP ★ v8.1

### 5-1. ERD 테이블 + 오케스트레이터 → 도메인 모듈 완전 매핑 ★ v7

| # | ERD 테이블 / 오케스트레이터 | 그룹 | Router 파일 | MVP 외부 API 노출 | 주요 메서드 |
|---|---|---|---|---|---|
| 1 | REGION | 공간/마을 | `region_router.py` | ✅ 조회 | `find_all`, `find_by_emd_code` |
| 2 | VILLAGE | 공간/마을 | `village_router.py` | ✅ 조회 | `find_all`, `find_by_code`, `find_by_region` |
| 3 | SNAP_POPULATION | 공공API 스냅샷 | `snap_population_router.py` | ✅ 조회 | `find_latest_by_village`, `find_history` |
| 4 | SNAP_BUILDING | 공공API 스냅샷 | `snap_building_router.py` | ✅ 조회 | `find_latest_by_village` |
| 5 | SNAP_TRANSPORT | 공공API 스냅샷 | `snap_transport_router.py` | ✅ 조회 | `find_latest_by_village` |
| 6 | SNAP_STATISTICS | 공공API 스냅샷 | `snap_statistics_router.py` | ✅ 조회 | `find_latest_by_village` |
| 7 | TVI_SCORE | TVI 산출 | `tvi_score_router.py` | ✅ 조회 | `find_latest_by_village`, `find_all_latest`, `find_danger_villages` |
| 8 | PRESCRIPTION_TYPE | 처방 라이브러리 | `prescription_type_router.py` | ✅ 조회 (백오피스) | `find_all_active`, `find_by_code` |
| 9 | PRESCRIPTION_INDICATOR | 처방 라이브러리 | `prescription_indicator_router.py` | ✅ 조회 (백오피스) | `find_by_prescription_type` |
| 10 | PRESCRIPTION_FUND_SOURCE | 처방 라이브러리 | `prescription_fund_source_router.py` | ✅ 조회 (백오피스) | `find_eligible_by_prescription_type` |
| 11 | DISPATCH_RULE | 처방 라이브러리 | `dispatch_rule_router.py` | ✅ 조회 (백오피스) | `find_all_active`, `find_by_indicator` |
| 12 | BUDGET_UNIT_PRICE | 처방 라이브러리 | `budget_unit_price_router.py` | ✅ 조회 (백오피스) | `find_by_prescription_type`, `find_latest_effective` |
| 13 | PRESCRIPTION_RESULT | 처방 결과 | `prescription_result_router.py` | ✅ 조회 + 생성 + SSE | `generate_for_village`, `stream_ai_description`, `find_by_village` |
| 14 | BUDGET_ESTIMATE | 처방 결과 | `budget_estimate_router.py` | ✅ 조회 + 생성 | `calculate_for_prescription`, `find_by_prescription_result` |
| 15 | ORGANIZATION | SaaS 운영 | `organization_router.py` | ✅ 조회 (인증 후) | `find_by_id`, `find_by_region_code` |
| 16 | SUBSCRIPTION | SaaS 운영 | `subscription_router.py` | ✅ 조회 (인증 후) | `find_active_by_org`, `check_tier` |
| 17 | USER | SaaS 운영 | `user_router.py` | ✅ 조회 + 로그인 | `login`, `find_by_organization_id`, `find_by_email`, `verify_password`, `update_last_login` |
| 18 | REPORT | SaaS 운영 | `report_router.py` | ✅ 생성 + 조회 | `generate`, `find_by_village`, `find_by_user` |
| 19 | DASHBOARD_ORCHESTRATOR | 대시보드 | `dashboard_orchestrator_router.py` | ✅ 집계 조회 | `get_summary`, `get_village_summary_card`, `get_alerts` |
| 20 | VILLAGE_DETAIL_ORCHESTRATOR | 마을 상세 | `village_detail_orchestrator_router.py` | ✅ 복합 조회 | `get_village_detail` (SNAP×4+TVI+처방 한번에) |
| 21 | REPORT_ORCHESTRATOR | 리포트 | `report_orchestrator_router.py` | ✅ 집계+생성 | `build_report_data` (village_detail 재사용) |
| 22 | PUBLIC_DATA_SYNC_ORCHESTRATOR | 배치/동기화 | `public_data_sync_orchestrator_router.py` | ✅ admin 트리거·이력 | `collect_all`, `ingest_fiscal_all`, `trigger_sync`, `get_latest_job` |

> **오케스트레이터 4개 설계 원칙 ★ v8.1**
> - 프랙탈 풀세트 유지 (12파일) — Entity, Output Port를 온전히 추가하여 도메인별 NeonDB Repository 단일 구현 보장 ★ v7
> - Interactor에서만 사용 — 다른 오케스트레이터의 Interactor를 직접 import 금지, Provider Depends 체이닝 주입
> - Repository는 읽기 집계 전용 (dashboard, village_detail) 또는 이력 저장 (report)
> - report_orchestrator는 village_detail_orchestrator를 Provider Depends 주입으로 재사용
> - public_data_sync_orchestrator는 화면용이 아닌 **배치/동기화 전용** 4번째 오케스트레이터 — 12파일 프랙탈 + VO 2종 + Provider APScheduler
> - sync Interactor는 타 도메인 **Output Port**만 주입 (Repository·UseCase Interactor 직접 import 금지)

> **SNAP_* 4개 라우터 설계 결정**: 파이프라인이 write 전담이지만, 조회 API는 외부에 노출.
> 이유: 대회 심사관·담당자가 "마을별 원본 데이터"를 직접 확인할 수 있어야 함.
> 배치 write: **APScheduler(Provider) → public_data_sync_orchestrator_interactor → Output Port → Repository.ingest_*()** (§10) ★ v8.1

### 5-2. v3 → v4 → v5 → v7 변경 대조표 ★ v7

| v3 라우터 (4개) | v4/v5/v7 개정 라우터 | 변경 이유 |
|---|---|---|
| `map_village_router.py` | `village_router.py` + `region_router.py` | REGION / VILLAGE 분리 (v4) |
| `dashboard_summary_router.py` | `tvi_score_router.py` | TVI 집계 = TVI_SCORE 단독 책임 (v4) |
| `prescription_chat_router.py` | `prescription_result_router.py` (AI 포함) + `prescription_type_router.py` + `prescription_indicator_router.py` + `prescription_fund_source_router.py` + `dispatch_rule_router.py` + `budget_unit_price_router.py` + `budget_estimate_router.py` | 7개 테이블 SRP 분리 (v4) |
| `report_generate_router.py` | `report_router.py` | REPORT 단독 책임 (v4) |
| (없음) | `dashboard_orchestrator_router.py` + `village_detail_orchestrator_router.py` + `report_orchestrator_router.py` | 화면 단위 데이터 조합용 오케스트레이터 3종 추가 (v5) 및 엔티티/포트 추가로 완벽 프랙탈화 완료 (v7) |
| (없음) | `prescription_result_port.py`로 AI 포트 병합 | 예외적인 `ai_text_generator_port.py` 제거로 100% 프랙탈 네이밍 정합 (v7) |
| `adapter/outbound/ai/gemini_ai_adapter.py` | `prescription_result_repository.py` 내부 | v7.1 |
| `adapter/outbound/pipeline/` 전체 | `{table}_repository.py` + matrix 2파일 | v8 |
| matrix batch 2파일 | `public_data_sync_orchestrator` 12파일 + Provider APScheduler | v8.1 |

### 5-3. v6 — ERD v5 정합 (현행): 공공API 9종 확정 + SRP/정규화 위반 수정 ★ v6~v8.3

> 출처: `TownPulse_API검증_작업요약.md`, `TownPulse_ERD_MVP_v6_1.md`. 대회 제출 전 "실연동 5개 공공API" 가정을 직접 점검한 결과 **5개 중 3개가 호출 불가능하거나 애초에 다른 데이터였음**이 드러나 출처를 교체하고, 9개 전체 활용신청 승인을 완료했다.

#### ① 출처 교체 3건

| 기존(깨짐) | 문제 | 교체 후 |
|---|---|---|
| `localdata.go.kr` | 2026.4.16 서비스 폐쇄 + 애초에 업종별 인허가정보(음식점·숙박업)였지 건축물대장과 무관 | 국토교통부_건축HUB_건축물대장정보 (`/getBrTitleInfo`) |
| `jumin.mois.go.kr` | CSV/xlsx 다운로드 전용 웹페이지, REST API 자체가 없었음 | 행안부 Open API 3종(인구·세대현황 / 성·연령별 인구수 / 인구이동현황) |
| `ktdb.go.kr` | 자료 신청·승인 포털(파일 제공) 구조, 보유 데이터도 여객/화물 O-D 조사였지 버스 배차간격 데이터가 아니었음 | `BusRouteInfoInqireService` (API#6, TAGO) |

#### ② SRP 위반 수정 — `registered_households`

기존 설계는 인구 도메인 값(전입세대수)을 `SNAP_BUILDING`(BuildingAdapter 전담 테이블)에 끼워 넣고 있었다 → 두 어댑터가 한 테이블을 나눠 쓰는 구조라 "어댑터 1:1 테이블" 원칙 위반.
→ **`SNAP_POPULATION`으로 이전.** `ingest_core_from_public_api()`(#2+#3) + `ingest_migration_from_public_api()`(#4, §10-8-1). ★ v9.0

#### ③ 정규화 위반 수정 — `fiscal_self_reliance`

재정자립도는 **시군구 단위** 지표인데 읍면동 단위 테이블(`SNAP_POPULATION`)에 두면 같은 시군 내 모든 읍면동이 값을 중복 저장하게 된다.
→ **`REGION` 테이블로 이전.** 연 1회 갱신이므로 SNAP_* 월간 파이프라인과도 분리(§10).

#### ③-2 정규화 — `birth_rate`·`daytime_population` ★ v8.4

조출생률·주간인구지수는 **시군구 단위** KOSIS(#8) 공표이며 법정동 직접 필드 없음.
→ **`REGION`으로 이전** (`fiscal_self_reliance`와 동일). `region_repository.ingest_kosis_sigungu_demographics()` — v1.0 ingest, **MVP TVI 미사용**.

#### ④ 지역코드 체계 통일 — 법정동코드(`bjdongCd`)가 메인 조인키

건축HUB·인구통계 API 응답을 직접 확인한 결과, 둘 다 **법정동코드**를 기본 축으로 사용한다. 인구통계 API는 법정동 축 조회 시 행정동코드(`행정기관코드`)가 구조적으로 자주 공란(법정동:행정동이 1:1 매칭이 아니기 때문)이라는 것도 실제 화면으로 검증했다.

| 코드 | 사용처 | REGION 필드 | 비고 |
|---|---|---|---|
| 법정동코드 | 건축HUB, 인구통계 3종 | `legal_dong_code` | ★ 메인 조인키 |
| 행정동코드 | (참조용) | `emd_code` | nullable, 공란 흔함 — 조인 키로 사용 금지 |
| 시군구코드 | 건축HUB | `sigungu_code` | 5자리 |
| TAGO 도시코드 | 버스 API cityCode | `tago_city_code` | getCtyCodeList — **§5-3⑥** 시드 표 참고. sigungu_code 직접 사용 불가 |

#### ⑥ TAGO `tago_city_code` 시드 — getCtyCodeList probe 확정 ★ v8.7

`BusRouteInfoInqireService/getCtyCodeList`는 **요청변수 없이 전국 목록**을 반환한다. `town.www/scripts/api_probe/endpoints.yaml`의 `tago_city_codes` probe로 실호출 후 `town.www/_docs/api_samples/tago_city_codes.json`에 저장하고, 충북(`citycode` 33xxx)만 추출한 `tago_city_codes_chungbuk.json`을 **시드 소스 SSOT**로 쓴다.

**충북 probe 결과 (2026-06-21, 10건):**

| `sigungu_name` | `tago_city_code` | 비고 |
|---|---|---|
| 청주시 | `33010` | getRouteNoList 118건 확인 |
| 충주시 | `33020` | |
| 제천시 | `33030` | |
| 보은군 | `33320` | |
| 옥천군 | `33330` | |
| 영동군 | `33340` | |
| 진천군 | `33350` | |
| 괴산군 | `33360` | |
| 음성군 | `33370` | |
| 단양군 | `33380` | |
| 증평군 | *(없음)* | TAGO 목록 미포함 — `tago_city_code` NULL 허용 |

> **주의:** 코드값을 문서에 추정 기재하지 말 것. probe JSON 키는 `citycode`·`cityname`(소문자). `REGION.sigungu_name`과 `cityname`이 일치하도록 시드한다.

```python
# town.www/scripts/seed/seed_tago_city_code.py — STEP 1 REGION 기본 행 시드 직후 1회
# tago_city_codes_chungbuk.json → UPDATE region SET tago_city_code = :code WHERE sigungu_name = :name
```

- `tago_city_code` NULL(증평군): `bus_route_count`·`avg_bus_interval_min`=**NULL** — `bus_route_count=0` 강제 금지. **15098534(GPS)** 는 §10-9-3대로 호출. 노선·배차는 미보유(§9-4)
- ERD `TownPulse_ERD_MVP_v6_1.md` §2 TAGO 표와 본 표를 동기화

#### ⑤ 버스 API — MVP ingest (노선 2단계 + 정류소)

**서비스 2종, 도메인 1개(`SNAP_TRANSPORT`)** — probe·샘플: `TownPulse_API필드검증_v2_0.md`, `town.www/_docs/api_samples/`.

| 단계 | 서비스 | operation | SNAP 필드 | 단위 |
|---|---|---|---|---|
| A | `BusRouteInfoInqireService` (#6, 15098529) | `getRouteNoList` | `bus_route_count` | 시/군 `tago_city_code` |
| B | 동일 | `getRouteInfoIem` | `avg_bus_interval_min` | 시/군 노선 `intervaltime` 평균 |
| C | `BusSttnInfoInqireService` (**15098534**, MVP) | `getCrdntPrxmtSttnList` | `nearest_stop_distance_m`, `bus_stops_within_1km` | **마을** `VILLAGE.lat/lng` |
| (보조) | #6 동일 신청 | `getRouteAcctoThrghSttnList` | 500m~1km 보강·`bus_stops_within_1km` | 시/군 노선별 GPS 카탈로그 (§10-9) |

**ingest 순서 (필수):** ① `village_repository.update_geocode_from_vworld()` → ② `snap_transport_repository.ingest_for_village(village_id)`  
정류소 API(`getCrdntPrxmtSttnList`)는 **반경 파라미터 없이 서버 고정 ~500m**만 반환 — 1km 컬럼은 §10-9 **노선 카탈로그 + 근접 API 병합** 알고리즘으로 산출.

```
A: tago_city_code → getRouteNoList → bus_route_count
B: routeId[] → getRouteInfoIem → avg_bus_interval_min
C: village(lat,lng) → getCrdntPrxmtSttnList → nearest_stop_distance_m, bus_stops_within_1km
```

**TVI:** 확정 교통 공백(`bus_route_count` 있음 + §9-4 `0.0`) → `bus_interval_score=0`. `tago_city_code` NULL(증평군)은 §9-4·§10-9-3 — **0 강제 금지**.

#### 최종 8개 API 확정 현황

| # | API | 매핑 테이블/필드 | 검증 상태 |
|---|---|---|---|
| 1 | 건축HUB_건축물대장정보(`/getBrTitleInfo`) | `SNAP_BUILDING.residential_buildings` | ✅ 요청·응답 probe 확정 |
| 2 | 인구·세대현황(법정동별) | `SNAP_POPULATION.population_total`, `registered_households` | ✅ |
| 3 | 성/연령별 인구수(법정동별) | `population_65plus`, `population_youth` | ✅ |
| 4 | 지역별 인구이동 현황 | `net_youth_migration` | ✅ |
| 5 | 지방재정365 재정자립도 | `REGION.fiscal_self_reliance` | ✅ (연1회, 일반회계, 자치단체=총계/전국·시도=순계) |
| 6 | 버스노선(`BusRouteInfoInqireService`) + 정류소(`BusSttnInfoInqireService`, **15098534**) | `bus_route_count`, `avg_bus_interval_min`, `nearest_stop_distance_m`, `bus_stops_within_1km` | ✅ 노선·정류소 probe 확정 |
| 7 | vworld | 지도 시각화 | ✅ |
| 8 | kosis | `SNAP_STATISTICS`(마을 grain) + `REGION.birth_rate`·`daytime_population`(시군구, v1.0) | ✅ |

> **번호 안내:** 구 스펙 API#8 vworld → **#7**, 구 API#9 kosis → **#8**. 구 API#7 TAGO 버스 = #6 통합.

> **남은 검증 (v1.0 전):** KOSIS tblId probe(`INH_1B81A01`, `DT_1JU1512` 등), `VACANCY_VERIFICATION`(시군구 sanity check).

---

## 6. 레이어별 코드 패턴

### 6-1. Domain — Entity (VILLAGE 예시)

```python
# domain/entities/village_entity.py
from dataclasses import dataclass

@dataclass(frozen=True)
class VillageEntity:
    id: str            # UUID
    region_id: str     # UUID
    name: str
    emd_code: str      # 10자리 행정코드
    lat: float
    lng: float
    last_synced_at: str  # ISO 8601 UTC
```

```python
# domain/entities/tvi_score_entity.py
from dataclasses import dataclass
from townpulse.domain.value_objects.tvi_grade_vo import TviGradeVO

@dataclass(frozen=True)
class TviScoreEntity:
    id: str
    village_id: str
    calculated_at: str
    tvi_score: float
    risk_level: str          # "danger" | "warning" | "safe"
    pop_decline_score: float
    vacancy_rate: float
    bus_interval_score: float
    prev_tvi_score: float
    tvi_delta: float
    model_version: str

    @property
    def tvi_grade(self) -> TviGradeVO:
        return TviGradeVO.from_score(self.tvi_score)
```

```python
# domain/entities/prescription_result_entity.py
from dataclasses import dataclass

@dataclass(frozen=True)
class PrescriptionResultEntity:
    id: str
    village_id: str
    tvi_score_id: str
    prescription_type_id: str
    priority_rank: int
    tvi_gain_min: float
    tvi_gain_max: float
    fund_applicable: bool
    ai_description: str | None   # Gemini 생성 — None이면 아직 미생성
    generated_at: str
```

### 6-2. Application — Input Port (TVI_SCORE 예시)

```python
# app/ports/input/tvi_score_use_case.py
from abc import ABC, abstractmethod
from townpulse.app.dtos.tvi_score_dto import (
    TviScoreLatestQuery, TviScoreLatestResult,
    TviScoreAllLatestQuery, TviScoreAllLatestResult,
    TviScoreDangerQuery, TviScoreDangerResult,
)

class TviScoreUseCase(ABC):
    @abstractmethod
    async def get_latest_by_village(
        self, query: TviScoreLatestQuery
    ) -> TviScoreLatestResult: ...

    @abstractmethod
    async def get_all_latest(
        self, query: TviScoreAllLatestQuery
    ) -> TviScoreAllLatestResult: ...

    @abstractmethod
    async def get_danger_villages(
        self, query: TviScoreDangerQuery
    ) -> TviScoreDangerResult: ...
```

```python
# app/ports/input/prescription_result_use_case.py
# ★ PRESCRIPTION_RESULT 전담 — AI 처방 생성 + 조회
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from townpulse.app.dtos.prescription_result_dto import (
    PrescriptionResultGenerateCommand, PrescriptionResultGenerateResult,
    PrescriptionResultStreamCommand,
    PrescriptionResultQueryByVillage, PrescriptionResultListResult,
)

class PrescriptionResultUseCase(ABC):
    @abstractmethod
    async def generate_for_village(
        self, command: PrescriptionResultGenerateCommand
    ) -> PrescriptionResultGenerateResult: ...

    @abstractmethod
    async def stream_ai_description(
        self, command: PrescriptionResultStreamCommand
    ) -> AsyncGenerator[str, None]: ...

    @abstractmethod
    async def find_by_village(
        self, query: PrescriptionResultQueryByVillage
    ) -> PrescriptionResultListResult: ...
```

### 6-3. Application — Output Port (분리 예시)

```python
# app/ports/output/prescription_type_port.py
from abc import ABC, abstractmethod
from townpulse.domain.entities.prescription_type_entity import PrescriptionTypeEntity

class PrescriptionTypePort(ABC):
    @abstractmethod
    async def find_all_active(self) -> list[PrescriptionTypeEntity]: ...

    @abstractmethod
    async def find_by_code(self, code: str) -> PrescriptionTypeEntity | None: ...

    @abstractmethod
    async def find_by_id(self, prescription_type_id: str) -> PrescriptionTypeEntity | None: ...  # ★ v8.6 SSE 컨텍스트 조립
```

```python
# app/ports/output/budget_estimate_port.py ★ v8.6
from abc import ABC, abstractmethod
from townpulse.domain.entities.budget_estimate_entity import BudgetEstimateEntity

class BudgetEstimatePort(ABC):
    @abstractmethod
    async def find_by_prescription_result_id(
        self, prescription_result_id: str
    ) -> BudgetEstimateEntity | None: ...
```

```python
# app/ports/output/dispatch_rule_port.py
from abc import ABC, abstractmethod
from townpulse.domain.entities.dispatch_rule_entity import DispatchRuleEntity

class DispatchRulePort(ABC):
    @abstractmethod
    async def find_all_active(self) -> list[DispatchRuleEntity]: ...

    @abstractmethod
    async def find_by_indicator(
        self, indicator_code: str
    ) -> list[DispatchRuleEntity]: ...
```

```python
# app/ports/output/prescription_result_port.py
# ★ v7: ai_text_generator_port.py를 삭제하고 AI 텍스트 생성 포트 역할까지 흡수 병합
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from townpulse.domain.entities.prescription_result_entity import PrescriptionResultEntity
from townpulse.domain.entities.dispatch_rule_entity import DispatchRuleEntity

class PrescriptionResultPort(ABC):
    @abstractmethod
    async def create_bulk(
        self, village_id: str, tvi_score_id: str, rules: list[DispatchRuleEntity]
    ) -> list[PrescriptionResultEntity]: ...

    @abstractmethod
    async def find_by_id(self, result_id: str) -> PrescriptionResultEntity | None: ...

    @abstractmethod
    async def find_by_village_id(self, village_id: str) -> list[PrescriptionResultEntity]: ...

    @abstractmethod
    async def stream_ai_description(
        self, system: str, messages: list[dict]
    ) -> AsyncGenerator[str, None]: ...
```

### 6-4. Application — Interactor (PRESCRIPTION_RESULT — AI 호출 포함) ★ v8.6

```python
# app/dtos/prescription_result_dto.py (발췌)
from dataclasses import dataclass

@dataclass(frozen=True)
class PrescriptionResultStreamCommand:
    prescription_result_id: str   # 라우터는 ID만 전달 — 프롬프트는 Interactor가 서버 조립 (§11-1b)
```

```python
# app/use_cases/prescription_result_interactor.py
from collections.abc import AsyncGenerator
from townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from townpulse.app.ports.output.prescription_result_port import PrescriptionResultPort
from townpulse.app.ports.output.dispatch_rule_port import DispatchRulePort
from townpulse.app.ports.output.village_port import VillagePort
from townpulse.app.ports.output.tvi_score_port import TviScorePort
from townpulse.app.ports.output.prescription_type_port import PrescriptionTypePort
from townpulse.app.ports.output.prescription_fund_source_port import PrescriptionFundSourcePort
from townpulse.app.ports.output.budget_estimate_port import BudgetEstimatePort
from townpulse.app.dtos.prescription_result_dto import (
    PrescriptionResultGenerateCommand, PrescriptionResultGenerateResult,
    PrescriptionResultStreamCommand,
    PrescriptionResultQueryByVillage, PrescriptionResultListResult,
    PrescriptionResultItem,
)
from core.matrix.grid_keymaker_secret_manager import TOWNPULSE_PRESCRIPTION_PERSONA

class PrescriptionResultInteractor(PrescriptionResultUseCase):
    def __init__(
        self,
        result_repo: PrescriptionResultPort,
        dispatch_repo: DispatchRulePort,
        village_repo: VillagePort,                    # ★ v8.6
        tvi_score_repo: TviScorePort,                  # ★ v8.6
        prescription_type_repo: PrescriptionTypePort,  # ★ v8.6
        fund_source_repo: PrescriptionFundSourcePort,  # ★ v8.6
        budget_estimate_repo: BudgetEstimatePort,      # ★ v8.6
    ) -> None:
        self._result_repo = result_repo
        self._dispatch_repo = dispatch_repo
        self._village_repo = village_repo
        self._tvi_score_repo = tvi_score_repo
        self._prescription_type_repo = prescription_type_repo
        self._fund_source_repo = fund_source_repo
        self._budget_estimate_repo = budget_estimate_repo

    async def generate_for_village(
        self, command: PrescriptionResultGenerateCommand
    ) -> PrescriptionResultGenerateResult:
        rules = await self._dispatch_repo.find_by_indicator(command.trigger_indicator)
        entities = await self._result_repo.create_bulk(
            village_id=command.village_id,
            tvi_score_id=command.tvi_score_id,
            rules=rules,
        )
        items = [
            PrescriptionResultItem(
                id=e.id,
                prescription_type_id=e.prescription_type_id,
                priority_rank=e.priority_rank,
                tvi_gain_min=e.tvi_gain_min,
                tvi_gain_max=e.tvi_gain_max,
                fund_applicable=e.fund_applicable,
                ai_description=e.ai_description,
                generated_at=e.generated_at,
            )
            for e in entities
        ]
        return PrescriptionResultGenerateResult(results=items, total=len(items))

    async def _build_context_prompt(self, result_id: str) -> str:
        """§11-1b — [데이터] 블록을 서버 측 엔티티 조회로만 조립."""
        result = await self._result_repo.find_by_id(result_id)
        if result is None:
            raise ValueError(f"PrescriptionResult {result_id} 없음")

        village = await self._village_repo.find_by_id(result.village_id)
        tvi = await self._tvi_score_repo.find_by_id(result.tvi_score_id)
        ptype = await self._prescription_type_repo.find_by_id(result.prescription_type_id)

        fund_text = "기금 매칭 정보 없음"
        if result.fund_applicable:
            funds = await self._fund_source_repo.find_eligible_by_prescription_type(
                result.prescription_type_id
            )
            if funds:
                fund_text = ", ".join(f"{f.fund_name}({f.fund_org})" for f in funds)

        budget_text = "예산 산정 전"
        estimate = await self._budget_estimate_repo.find_by_prescription_result_id(result_id)
        if estimate:
            budget_text = (
                f"{estimate.budget_min:,}만원 ~ {estimate.budget_max:,}만원"
                f" (근거: {estimate.calculation_note})"
            )

        return f"""[데이터]
마을: {village.name}
TVI 점수: {tvi.tvi_score} ({tvi.risk_level})
처방: {ptype.name} ({ptype.category}), 우선순위 {result.priority_rank}순위
TVI 기대 개선폭: {result.tvi_gain_min} ~ {result.tvi_gain_max}
예산: {budget_text}
기금 출처: {fund_text}

위 [데이터]만 근거로 설명을 작성하세요. 위에 없는 숫자는 절대 만들지 마세요."""

    async def stream_ai_description(
        self, command: PrescriptionResultStreamCommand
    ) -> AsyncGenerator[str, None]:
        context_prompt = await self._build_context_prompt(command.prescription_result_id)
        messages = [{"role": "user", "content": context_prompt}]
        async for chunk in self._result_repo.stream_ai_description(
            system=TOWNPULSE_PRESCRIPTION_PERSONA,
            messages=messages,
        ):
            yield chunk

    async def find_by_village(
        self, query: PrescriptionResultQueryByVillage
    ) -> PrescriptionResultListResult:
        entities = await self._result_repo.find_by_village_id(query.village_id)
        items = [
            PrescriptionResultItem(
                id=e.id,
                prescription_type_id=e.prescription_type_id,
                priority_rank=e.priority_rank,
                tvi_gain_min=e.tvi_gain_min,
                tvi_gain_max=e.tvi_gain_max,
                fund_applicable=e.fund_applicable,
                ai_description=e.ai_description,
                generated_at=e.generated_at,
            )
            for e in entities
        ]
        return PrescriptionResultListResult(results=items, total=len(items))
```

> `prescription_result_provider.py` — Interactor 조립 시 위 6개 Port 주입. ★ v8.6

### 6-5. Application — Interactor (TVI_SCORE — 대시보드 집계)

```python
# app/use_cases/tvi_score_interactor.py
# ★ v4: v3의 dashboard_summary_interactor 역할이 여기로 통합
from townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from townpulse.app.ports.output.tvi_score_port import TviScorePort
from townpulse.app.dtos.tvi_score_dto import (
    TviScoreLatestQuery, TviScoreLatestResult, TviScoreLatestItem,
    TviScoreAllLatestQuery, TviScoreAllLatestResult,
    TviScoreDangerQuery, TviScoreDangerResult,
)

class TviScoreInteractor(TviScoreUseCase):
    def __init__(self, repository: TviScorePort) -> None:
        self._repository = repository

    async def get_latest_by_village(
        self, query: TviScoreLatestQuery
    ) -> TviScoreLatestResult:
        entity = await self._repository.find_latest_by_village(query.village_id)
        if entity is None:
            return TviScoreLatestResult(score=None, found=False)
        grade = entity.tvi_grade
        return TviScoreLatestResult(
            score=TviScoreLatestItem(
                id=entity.id,
                village_id=entity.village_id,
                tvi_score=entity.tvi_score,
                tvi_grade=grade.grade.value,
                tvi_label=grade.label,
                color_hex=grade.color_hex,
                tvi_delta=entity.tvi_delta,
                risk_level=entity.risk_level,
                calculated_at=entity.calculated_at,
                model_version=entity.model_version,
            ),
            found=True,
        )

    async def get_all_latest(
        self, query: TviScoreAllLatestQuery
    ) -> TviScoreAllLatestResult:
        entities = await self._repository.find_all_latest(
            grade_filter=query.grade_filter,
            sigun_filter=query.sigun_filter,
        )
        # grade_filter는 Interactor에서 처리
        if query.grade_filter:
            entities = [
                e for e in entities
                if e.tvi_grade.grade.value == query.grade_filter
            ]
        items = [
            TviScoreLatestItem(
                id=e.id,
                village_id=e.village_id,
                tvi_score=e.tvi_score,
                tvi_grade=e.tvi_grade.grade.value,
                tvi_label=e.tvi_grade.label,
                color_hex=e.tvi_grade.color_hex,
                tvi_delta=e.tvi_delta,
                risk_level=e.risk_level,
                calculated_at=e.calculated_at,
                model_version=e.model_version,
            )
            for e in entities
        ]
        return TviScoreAllLatestResult(
            scores=items,
            total=len(items),
            danger_count=sum(1 for i in items if i.tvi_grade == "danger"),
            warning_count=sum(1 for i in items if i.tvi_grade == "warning"),
            safe_count=sum(1 for i in items if i.tvi_grade == "safe"),
            avg_tvi_score=round(
                sum(i.tvi_score for i in items) / len(items), 2
            ) if items else 0.0,
        )

    async def get_danger_villages(
        self, query: TviScoreDangerQuery
    ) -> TviScoreDangerResult:
        entities = await self._repository.find_danger_villages(
            threshold=query.threshold
        )
        return TviScoreDangerResult(
            villages=[e.village_id for e in entities],
            total=len(entities),
        )
```

### 6-6. Inbound Adapter — Router (18개 패턴)

```python
# adapter/inbound/api/v1/tvi_score_router.py
# ★ v4: v3의 map_village_router + dashboard_summary_router 역할 통합 → TVI_SCORE 전담
from fastapi import APIRouter, Depends, Query
from townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from townpulse.adapter.inbound.api.schemas.tvi_score_schema import (
    TviScoreLatestResponseSchema,
    TviScoreAllLatestResponseSchema,
)
from townpulse.adapter.inbound.mappers.tvi_score_mapper import TviScoreMapper
from townpulse.dependencies.tvi_score_provider import get_tvi_score_use_case

router = APIRouter(prefix="/tvi-scores", tags=["tvi-score"])

@router.get("/{village_id}/latest", response_model=TviScoreLatestResponseSchema)
async def get_latest_by_village(
    village_id: str,
    use_case: TviScoreUseCase = Depends(get_tvi_score_use_case),
) -> TviScoreLatestResponseSchema:
    query = TviScoreMapper.to_latest_query(village_id)
    result = await use_case.get_latest_by_village(query)
    return TviScoreMapper.to_latest_response_schema(result)

@router.get("", response_model=TviScoreAllLatestResponseSchema)
async def get_all_latest(
    grade: str | None = Query(None),
    sigun: str | None = Query(None),
    use_case: TviScoreUseCase = Depends(get_tvi_score_use_case),
) -> TviScoreAllLatestResponseSchema:
    query = TviScoreMapper.to_all_latest_query(grade, sigun)
    result = await use_case.get_all_latest(query)
    return TviScoreMapper.to_all_latest_response_schema(result)
```

```python
# adapter/inbound/api/v1/prescription_result_router.py
# ★ PRESCRIPTION_RESULT 전담 — AI 처방 생성 + SSE 스트리밍 + 이력 조회
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from townpulse.adapter.inbound.api.schemas.prescription_result_schema import (
    PrescriptionResultGenerateRequestSchema,
    PrescriptionResultGenerateResponseSchema,
    PrescriptionResultListResponseSchema,
)
from townpulse.adapter.inbound.mappers.prescription_result_mapper import PrescriptionResultMapper
from townpulse.dependencies.prescription_result_provider import get_prescription_result_use_case

router = APIRouter(prefix="/prescription-results", tags=["prescription-result"])

@router.post("", response_model=PrescriptionResultGenerateResponseSchema)
async def generate_for_village(
    body: PrescriptionResultGenerateRequestSchema,
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
) -> PrescriptionResultGenerateResponseSchema:
    command = PrescriptionResultMapper.to_generate_command(body)
    result = await use_case.generate_for_village(command)
    return PrescriptionResultMapper.to_generate_response_schema(result)

@router.get("/{prescription_result_id}/stream")
async def stream_ai_description(
    prescription_result_id: str,
    token: str = Query(...),
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
) -> StreamingResponse:
    command = PrescriptionResultMapper.to_stream_command(
        prescription_result_id=prescription_result_id
    )
    async def event_generator():
        async for chunk in use_case.stream_ai_description(command):
            yield f"data: {chunk}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/by-village/{village_id}", response_model=PrescriptionResultListResponseSchema)
async def find_by_village(
    village_id: str,
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
) -> PrescriptionResultListResponseSchema:
    query = PrescriptionResultMapper.to_query_by_village(village_id)
    result = await use_case.find_by_village(query)
    return PrescriptionResultMapper.to_list_response_schema(result)
```

```python
# adapter/inbound/api/v1/dispatch_rule_router.py
# ★ DISPATCH_RULE 전담 — 처방 조건 조회 (백오피스)
from fastapi import APIRouter, Depends, Query
from townpulse.app.ports.input.dispatch_rule_use_case import DispatchRuleUseCase
from townpulse.adapter.inbound.api.schemas.dispatch_rule_schema import DispatchRuleListResponseSchema
from townpulse.adapter.inbound.mappers.dispatch_rule_mapper import DispatchRuleMapper
from townpulse.dependencies.dispatch_rule_provider import get_dispatch_rule_use_case

router = APIRouter(prefix="/dispatch-rules", tags=["dispatch-rule"])

@router.get("", response_model=DispatchRuleListResponseSchema)
async def find_all_active(
    indicator: str | None = Query(None),
    use_case: DispatchRuleUseCase = Depends(get_dispatch_rule_use_case),
) -> DispatchRuleListResponseSchema:
    query = DispatchRuleMapper.to_query(indicator)
    result = await use_case.find_all_active(query)
    return DispatchRuleMapper.to_list_response_schema(result)
```

### 6-7. Router 집계 (__init__.py) ★ v4 핵심

```python
# adapter/inbound/api/__init__.py
from fastapi import APIRouter
from townpulse.adapter.inbound.api.v1.region_router import router as region_router
from townpulse.adapter.inbound.api.v1.village_router import router as village_router
from townpulse.adapter.inbound.api.v1.snap_population_router import router as snap_population_router
from townpulse.adapter.inbound.api.v1.snap_building_router import router as snap_building_router
from townpulse.adapter.inbound.api.v1.snap_transport_router import router as snap_transport_router
from townpulse.adapter.inbound.api.v1.snap_statistics_router import router as snap_statistics_router
from townpulse.adapter.inbound.api.v1.tvi_score_router import router as tvi_score_router
from townpulse.adapter.inbound.api.v1.prescription_type_router import router as prescription_type_router
from townpulse.adapter.inbound.api.v1.prescription_indicator_router import router as prescription_indicator_router
from townpulse.adapter.inbound.api.v1.prescription_fund_source_router import router as prescription_fund_source_router
from townpulse.adapter.inbound.api.v1.dispatch_rule_router import router as dispatch_rule_router
from townpulse.adapter.inbound.api.v1.budget_unit_price_router import router as budget_unit_price_router
from townpulse.adapter.inbound.api.v1.prescription_result_router import router as prescription_result_router
from townpulse.adapter.inbound.api.v1.budget_estimate_router import router as budget_estimate_router
from townpulse.adapter.inbound.api.v1.organization_router import router as organization_router
from townpulse.adapter.inbound.api.v1.subscription_router import router as subscription_router
from townpulse.adapter.inbound.api.v1.user_router import router as user_router
from townpulse.adapter.inbound.api.v1.report_router import router as report_router

townpulse_router = APIRouter(prefix="/townpulse")

# 공간/마을
townpulse_router.include_router(region_router)
townpulse_router.include_router(village_router)
# 공공API 스냅샷
townpulse_router.include_router(snap_population_router)
townpulse_router.include_router(snap_building_router)
townpulse_router.include_router(snap_transport_router)
townpulse_router.include_router(snap_statistics_router)
# TVI 산출
townpulse_router.include_router(tvi_score_router)
# 처방 라이브러리
townpulse_router.include_router(prescription_type_router)
townpulse_router.include_router(prescription_indicator_router)
townpulse_router.include_router(prescription_fund_source_router)
townpulse_router.include_router(dispatch_rule_router)
townpulse_router.include_router(budget_unit_price_router)
# 처방 결과
townpulse_router.include_router(prescription_result_router)
townpulse_router.include_router(budget_estimate_router)
# SaaS 운영
townpulse_router.include_router(organization_router)
townpulse_router.include_router(subscription_router)
townpulse_router.include_router(user_router)
townpulse_router.include_router(report_router)
# 오케스트레이터 (★ v5 — 화면 단위 집계, Interactor에서만 사용)
townpulse_router.include_router(dashboard_orchestrator_router)
townpulse_router.include_router(village_detail_orchestrator_router)
townpulse_router.include_router(report_orchestrator_router)
townpulse_router.include_router(public_data_sync_orchestrator_router)  # ★ v8.1

# 최종 URL 예시 (18개 단일 도메인):
# GET  /api/townpulse/tvi-scores?grade=danger
# POST /api/townpulse/prescription-results
# GET  /api/townpulse/prescription-results/{id}/stream?token=JWT
# 최종 URL 예시 (4개 오케스트레이터 ★ v8.1):
# GET  /api/townpulse/dashboard/summary
# GET  /api/townpulse/village-detail/{village_code}
# POST /api/townpulse/report-data/{village_code}
# POST /api/townpulse/admin/sync/trigger
```

### 6-8. Dependencies — Provider (PRESCRIPTION_RESULT 예시)

```python
# dependencies/prescription_result_provider.py
# ★ v7.1: PrescriptionResultPort + DispatchRulePort 2개만 Interactor에 주입
#     Gemini는 Repository 내부 private 메서드 — 별도 adapter 파일·주입 없음 (12파일 프랙탈)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.matrix.grid_oracle_database_manager import get_db
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from townpulse.app.use_cases.prescription_result_interactor import PrescriptionResultInteractor
from townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository
from townpulse.adapter.outbound.repositories.dispatch_rule_repository import DispatchRuleRepository

async def get_prescription_result_use_case(
    db: AsyncSession = Depends(get_db),
) -> PrescriptionResultUseCase:
    result_repo = PrescriptionResultRepository(session=db, keymaker=get_keymaker())
    dispatch_repo = DispatchRuleRepository(session=db)

    return PrescriptionResultInteractor(
        result_repo=result_repo,
        dispatch_repo=dispatch_repo,
    )
```

```python
# dependencies/tvi_score_provider.py
# ★ v4: TVI_SCORE 전담 Provider (대시보드 집계 포함)
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.matrix.grid_oracle_database_manager import get_db
from townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from townpulse.app.use_cases.tvi_score_interactor import TviScoreInteractor
from townpulse.adapter.outbound.repositories.tvi_score_repository import TviScoreRepository

async def get_tvi_score_use_case(
    db: AsyncSession = Depends(get_db),
) -> TviScoreUseCase:
    repository = TviScoreRepository(session=db)
    return TviScoreInteractor(repository=repository)
```

### 6-9. Morpheus — 오케스트레이터 Interactor 공통 베이스 ★ v7

오케스트레이터 4종(`dashboard_`, `village_detail_`, `report_`, `public_data_sync_orchestrator_interactor`)은 **`grid_morpheus_base_orchestrator.py`** 를 상속합니다. 화면용 3종은 `asyncio.gather` 병렬 조회, sync는 **순차 ingest** (rate limit).

```python
# core/matrix/grid_morpheus_base_orchestrator.py
"""오케스트레이터 Interactor 공통 베이스 — asyncio.gather 래퍼 (Morpheus)."""

from __future__ import annotations

import asyncio
from typing import Any


class MorpheusOrchestratorBase:
    async def gather_use_cases(self, *awaitables: Any) -> list[Any]:
        """UseCase Port 병렬 호출 — 예외는 첫 실패에서 전파."""
        return list(await asyncio.gather(*awaitables))
```

```python
# app/use_cases/dashboard_orchestrator_interactor.py (발췌)
from core.matrix.grid_morpheus_base_orchestrator import MorpheusOrchestratorBase

class DashboardOrchestratorInteractor(MorpheusOrchestratorBase):
    async def get_summary(self, query: DashboardQueryDto) -> DashboardSummaryResultDto:
        tvi, villages, building, transport = await self.gather_use_cases(
            self._tvi_use_case.get_all_latest(...),
            self._village_use_case.find_all(...),
            ...
        )
        ...
```

---

## 7. API 엔드포인트 (22개 도메인)

모든 경로 prefix: `/api/townpulse/`

### 공간/마을 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| GET | `/api/townpulse/regions` | 필요 | 충북 행정구역 전체 | REGION |
| GET | `/api/townpulse/regions/{emd_code}` | 필요 | 행정구역 상세 | REGION |
| GET | `/api/townpulse/villages` | 필요 | 마을 전체 목록 | VILLAGE |
| GET | `/api/townpulse/villages/{emd_code}` | 필요 | 마을 상세 | VILLAGE |
| GET | `/api/townpulse/villages/by-region/{region_id}` | 필요 | 행정구역별 마을 | VILLAGE |

### 공공API 스냅샷 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| GET | `/api/townpulse/snap/population/{village_id}/latest` | 필요 | 최신 인구 스냅샷 | SNAP_POPULATION |
| GET | `/api/townpulse/snap/population/{village_id}/history` | 필요 | 인구 스냅샷 이력 | SNAP_POPULATION |
| GET | `/api/townpulse/snap/building/{village_id}/latest` | 필요 | 최신 건물 스냅샷 | SNAP_BUILDING |
| GET | `/api/townpulse/snap/transport/{village_id}/latest` | 필요 | 최신 교통 스냅샷 | SNAP_TRANSPORT |
| GET | `/api/townpulse/snap/statistics/{village_id}/latest` | 필요 | 최신 통계 스냅샷 | SNAP_STATISTICS |

### TVI 산출 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| GET | `/api/townpulse/tvi-scores` | 필요 | 전체 마을 최신 TVI (히트맵용, 필터: grade, sigun) | TVI_SCORE |
| GET | `/api/townpulse/tvi-scores/{village_id}/latest` | 필요 | 마을 최신 TVI + 대시보드 집계 | TVI_SCORE |
| GET | `/api/townpulse/tvi-scores/danger` | 필요 | 소멸위험 마을 목록 | TVI_SCORE |

### 처방 라이브러리 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| GET | `/api/townpulse/prescription-types` | 필요 | 처방 유형 전체 | PRESCRIPTION_TYPE |
| GET | `/api/townpulse/prescription-types/{code}` | 필요 | 처방 유형 상세 | PRESCRIPTION_TYPE |
| GET | `/api/townpulse/prescription-indicators` | 필요 | 처방-지표 매핑 | PRESCRIPTION_INDICATOR |
| GET | `/api/townpulse/prescription-fund-sources` | 필요 | 처방-기금 매핑 | PRESCRIPTION_FUND_SOURCE |
| GET | `/api/townpulse/dispatch-rules` | 필요 | 처방 자동 매핑 조건 | DISPATCH_RULE |
| GET | `/api/townpulse/budget-unit-prices` | 필요 | 예산 단가 라이브러리 | BUDGET_UNIT_PRICE |

### 처방 결과 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| POST | `/api/townpulse/prescription-results` | **쓰기** | 마을 처방 생성 (`require_write_scope`) | PRESCRIPTION_RESULT |
| GET | `/api/townpulse/prescription-results/{id}/stream` | SSE+JWT | AI 설명 스트리밍 | PRESCRIPTION_RESULT |
| GET | `/api/townpulse/prescription-results/by-village/{village_id}` | 필요 | 마을 처방 이력 | PRESCRIPTION_RESULT |
| POST | `/api/townpulse/budget-estimates` | **쓰기** | 처방별 예산 산출 (`require_write_scope`) | BUDGET_ESTIMATE |
| GET | `/api/townpulse/budget-estimates/by-prescription/{prescription_result_id}` | 필요 | 처방별 예산 조회 | BUDGET_ESTIMATE |

### SaaS 운영 그룹

| Method | 경로 | 인증 | 설명 | 담당 테이블 |
|---|---|---|---|---|
| GET | `/api/townpulse/organizations/{id}` | 필요 | 기관 조회 | ORGANIZATION |
| GET | `/api/townpulse/subscriptions/my` | 필요 | 내 기관 구독 조회 | SUBSCRIPTION |
| POST | `/api/townpulse/users/login` | 없음 | 로그인 (JWT 발급) — 요청·응답 §12-1c | USER |
| POST | `/api/townpulse/users/demo/token` | 없음 | 데모 읽기전용 JWT 즉시 발급 (§12-1b) | USER |
| GET | `/api/townpulse/users/me` | 필요 | 내 정보 | USER |
| POST | `/api/townpulse/reports` | **쓰기** | 리포트 생성 (`require_write_scope`) | REPORT |
| GET | `/api/townpulse/reports/by-village/{village_id}` | 필요 | 마을 리포트 이력 | REPORT |

### 오케스트레이터 그룹 ★ v5

| Method | 경로 | 인증 | 설명 | 담당 오케스트레이터 |
|---|---|---|---|---|
| GET | `/api/townpulse/dashboard/summary` | 필요 | D-02 대시보드 집계 (카드 4개+TOP5+알림) | DASHBOARD_ORCH |
| GET | `/api/townpulse/dashboard/map/villages` | 필요 | D-03 전체 마을 좌표+TVI+등급 (히트맵용) | DASHBOARD_ORCH |
| GET | `/api/townpulse/dashboard/map/villages/{village_code}` | 필요 | D-03 마을 클릭 요약 카드 | DASHBOARD_ORCH |
| GET | `/api/townpulse/village-detail/{village_code}` | 필요 | D-04+M-03 마을 상세 (SNAP×4+TVI+처방 상위2) | VILLAGE_DETAIL_ORCH |
| POST | `/api/townpulse/report-data/{village_code}` | **쓰기** | D-06+M-05 리포트 데이터 집계 (`require_write_scope`) | REPORT_ORCH |
| POST | `/api/townpulse/admin/sync/trigger` | **쓰기** (admin) | 수동 배치 트리거 (`require_write_scope`) | PUBLIC_DATA_SYNC_ORCH |
| GET | `/api/townpulse/admin/sync/jobs/latest` | 필요 (admin) | 최근 동기화 job 이력 | PUBLIC_DATA_SYNC_ORCH |
| GET | `/api/townpulse/admin/sync/jobs/{job_id}` | 필요 (admin) | job 상세 | PUBLIC_DATA_SYNC_ORCH |

---

## 8. 데이터베이스 스키마

ERD 18개 테이블 — SQL 전체 정의

```sql
-- 1. REGION  ★ v6: 코드체계 4종 + 재정자립도(정규화 위반 수정으로 이전) 반영
CREATE TABLE region (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    sido                 VARCHAR(20)  NOT NULL,
    sigungu              VARCHAR(50)  NOT NULL,
    sigungu_code         VARCHAR(5),                  -- 건축HUB·버스노선(메인) 호출용
    emd_name             VARCHAR(100) NOT NULL,
    emd_code             VARCHAR(10)  UNIQUE,          -- 행정동코드 — nullable (법정동 축 조회시 공란 흔함, 참조용)
    legal_dong_code      VARCHAR(10)  NOT NULL UNIQUE, -- ★메인 조인키 — 건축HUB·인구통계 3종 공통(bjdongCd)
    tago_city_code       VARCHAR(10),                  -- 버스 API cityCode (TAGO getCtyCodeList)
    area_km2             FLOAT,
    fiscal_self_reliance FLOAT,                        -- 시군구 단위, 연1회 갱신, 일반회계·자치단체 총계 기준
    fiscal_data_year     DATE,
    birth_rate           FLOAT,                        -- KOSIS #8, 시군구, v1.0 ingest ★ v8.4
    daytime_population   FLOAT,                        -- KOSIS #8, 시군구, 5년 주기 ★ v8.4
    demographic_data_year DATE                         -- birth/daytime 기준 연도 ★ v8.4
);

-- 2. VILLAGE
CREATE TABLE village (
    id             UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    region_id      UUID         NOT NULL REFERENCES region(id),
    name           VARCHAR(100) NOT NULL,
    emd_code       VARCHAR(10)  NOT NULL UNIQUE,
    lat            FLOAT,
    lng            FLOAT,
    last_synced_at TIMESTAMP
);

-- 3. SNAP_POPULATION  ★ v6: registered_households 편입(SRP 수정) / fiscal_self_reliance REGION으로 이전(정규화 수정)
CREATE TABLE snap_population (
    id                    UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id            UUID    NOT NULL REFERENCES village(id),
    snapshot_date         DATE    NOT NULL,
    population_total      INTEGER,                -- API#2 인구·세대현황(법정동별)
    population_65plus     INTEGER,                -- API#3 성/연령별 인구수(법정동별)
    population_youth      INTEGER,                -- API#3 동일
    registered_households INTEGER,                -- API#2의 세대수 필드 — SNAP_BUILDING에서 이전(SRP) ★ v6
    net_youth_migration   INTEGER,                -- API#4 지역별 인구이동현황
    fetched_at            TIMESTAMP DEFAULT NOW()
);

-- 4. SNAP_BUILDING  ★ v6: registered_households 제거 (SNAP_POPULATION으로 이전, SRP 수정)
CREATE TABLE snap_building (
    id                    UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id            UUID    NOT NULL REFERENCES village(id),
    snapshot_date         DATE    NOT NULL,
    residential_buildings INTEGER,    -- API#1 건축HUB 표제부, mainPurpsCdNm 화이트리스트 COUNT
    fetched_at            TIMESTAMP DEFAULT NOW()
);

-- 5. SNAP_TRANSPORT
CREATE TABLE snap_transport (
    id                         UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id                 UUID    NOT NULL REFERENCES village(id),
    snapshot_date              DATE    NOT NULL,
    bus_route_count            INTEGER,                -- API#6 getRouteNoList (시/군)
    avg_bus_interval_min       FLOAT,                  -- API#6 getRouteInfoIem 평균(평일)
    nearest_stop_distance_m    INTEGER,                -- API 15098534 + vworld 좌표 (MVP)
    bus_stops_within_1km       INTEGER,                -- §10-9: 15098534+노선카탈로그 Haversine
    fetched_at                 TIMESTAMP DEFAULT NOW()
);

-- 6. SNAP_STATISTICS
CREATE TABLE snap_statistics (
    id            UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id    UUID    NOT NULL REFERENCES village(id),
    snapshot_date DATE    NOT NULL,
    aging_ratio   FLOAT,
    youth_ratio   FLOAT,
    pop_density   FLOAT,
    fetched_at    TIMESTAMP DEFAULT NOW()
);

-- 7. TVI_SCORE
CREATE TABLE tvi_score (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id        UUID        NOT NULL REFERENCES village(id),
    calculated_at     DATE        NOT NULL,
    tvi_score         FLOAT       NOT NULL,
    risk_level        VARCHAR(10) NOT NULL,  -- "danger"|"warning"|"safe"
    pop_decline_score FLOAT,
    vacancy_rate      FLOAT,
    bus_interval_score FLOAT,
    prev_tvi_score    FLOAT,
    tvi_delta         FLOAT,
    model_version     VARCHAR(50) DEFAULT 'weighted_sum_v1'
);

-- 8. PRESCRIPTION_TYPE
CREATE TABLE prescription_type (
    id               UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    code             VARCHAR(50)  NOT NULL UNIQUE,
    name             VARCHAR(100) NOT NULL,
    category         VARCHAR(50),
    rollout_timeline VARCHAR(20),  -- "urgent"|"medium"|"long"
    is_active        BOOLEAN DEFAULT TRUE
);

-- 9. PRESCRIPTION_INDICATOR
CREATE TABLE prescription_indicator (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_type_id UUID        NOT NULL REFERENCES prescription_type(id),
    indicator_code       VARCHAR(50) NOT NULL,
    effect_direction     VARCHAR(20) NOT NULL  -- "positive"|"negative"
);

-- 10. PRESCRIPTION_FUND_SOURCE
CREATE TABLE prescription_fund_source (
    id                   UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_type_id UUID         NOT NULL REFERENCES prescription_type(id),
    fund_name            VARCHAR(200) NOT NULL,
    fund_org             VARCHAR(100),
    is_eligible          BOOLEAN DEFAULT TRUE
);

-- 11. DISPATCH_RULE
CREATE TABLE dispatch_rule (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_type_id UUID        NOT NULL REFERENCES prescription_type(id),
    trigger_indicator    VARCHAR(50) NOT NULL,
    operator             VARCHAR(10) NOT NULL,  -- "gt"|"lt"|"gte"|"lte"
    threshold_value      FLOAT       NOT NULL,
    priority_rank        INTEGER     NOT NULL
);

-- 12. BUDGET_UNIT_PRICE
CREATE TABLE budget_unit_price (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_type_id UUID        NOT NULL REFERENCES prescription_type(id),
    unit                 VARCHAR(20) NOT NULL,
    price_min            BIGINT      NOT NULL,  -- 만원 단위
    price_max            BIGINT      NOT NULL,
    reference_source     VARCHAR(300),
    effective_from       DATE        NOT NULL
);

-- 13. PRESCRIPTION_RESULT
CREATE TABLE prescription_result (
    id                   UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    village_id           UUID      NOT NULL REFERENCES village(id),
    tvi_score_id         UUID      NOT NULL REFERENCES tvi_score(id),
    prescription_type_id UUID      NOT NULL REFERENCES prescription_type(id),
    priority_rank        INTEGER   NOT NULL,
    tvi_gain_min         FLOAT,
    tvi_gain_max         FLOAT,
    fund_applicable      BOOLEAN   DEFAULT FALSE,
    ai_description       TEXT,
    generated_at         TIMESTAMP DEFAULT NOW()
);

-- 14. BUDGET_ESTIMATE
CREATE TABLE budget_estimate (
    id                    UUID      PRIMARY KEY DEFAULT gen_random_uuid(),
    prescription_result_id UUID     NOT NULL REFERENCES prescription_result(id),
    budget_unit_price_id  UUID      NOT NULL REFERENCES budget_unit_price(id),
    quantity              INTEGER   NOT NULL,
    budget_min            BIGINT    NOT NULL,  -- 만원 단위
    budget_max            BIGINT    NOT NULL,
    calculation_note      TEXT
);

-- 15. ORGANIZATION
CREATE TABLE organization (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    org_type    VARCHAR(50),
    region_code VARCHAR(10),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- 16. SUBSCRIPTION
CREATE TABLE subscription (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID        NOT NULL REFERENCES organization(id),
    tier            VARCHAR(20) NOT NULL,  -- "basic"|"standard"|"premium"
    started_at      DATE        NOT NULL,
    expires_at      DATE,
    is_active       BOOLEAN DEFAULT TRUE,
    monthly_fee     BIGINT
);

-- 17. USER (예약어 충돌 방지: townpulse_user)
CREATE TABLE townpulse_user (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID        NOT NULL REFERENCES organization(id),
    name            VARCHAR(100),
    email           VARCHAR(200) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,  -- bcrypt — §12-1c ★ v9.1
    role            VARCHAR(20) DEFAULT 'viewer',
    last_login_at   TIMESTAMP
);

-- 18. REPORT
CREATE TABLE report (
    id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID        NOT NULL REFERENCES townpulse_user(id),
    village_id   UUID        NOT NULL REFERENCES village(id),
    tvi_score_id UUID        NOT NULL REFERENCES tvi_score(id),
    title        VARCHAR(300),
    format       VARCHAR(20) DEFAULT 'pdf',
    file_url     VARCHAR(1000),
    generated_at TIMESTAMP DEFAULT NOW()
);

-- 9. TVI 산출 공식 — 상세는 본문 §9 참조 (v8.5: min-max 정규화 + 처방 역산)

---

## 9. TVI 산출 공식 ★ v8.5 → v8.8 경계 명문화

> 구현 위치: `tvi_score_repository.recalculate_all()` private — **별도 `tvi_calculator` 모듈·`simulate_tvi_gain.py` 독립 파일 금지** (v8 SRP).  
> 처방 TVI 기대치: `prescription_result_repository.generate_for_village()` → `simulate_tvi_gain()` (동일 §9 재호출).

### 9-0. SSOT 범위 — 외부 TVI 시뮬레이션 검토 (채택·비채택) ★ v8.8

| 구분 | 내용 |
|---|---|
| **채택** | 종합 TVI `0.70 / 0.20 / 0.10` · 등급 30/60 · `pop_decline_score` 5지표 **min-max** · 교통 공백 = §9-4 `calculate_bus_interval_score` (**증평형 절충** ★ v9.4) · `simulate_tvi_gain()` 동일 `calculate_tvi()` · **INCENTIVE γ·SOC 빈집 연계** §9-5 ★ v9.5 |
| **비채택** | `vacancy_score`·`bus_interval_score`에 min-max 적용(§9-4 **선형식** 유지) · DRT가 `nearest_stop_distance_m`·`bus_stops_within_1km` 즉시 변경 · Studio 등 **외부 리포트·차트·구체 소수점**(12.1, 93.3, +9.3 등)을 SSOT로 고정 · 법정동 10건 부분 표본 min-max(전체 228 표본만 사용) · **min/max EMA 완만화·Baseline Anchor** — MVP이후 `TownPulse_백엔드_MVP이후_개발정의서_v4_0.md` §1-1 |

데모 시나리오(단양군 영춘면 TVI **12**, 1.2km·1km 내 정류장 0)는 와이어프레임·사업정의서 §5-4 **정성 예시**로만 유지합니다. 정류장 1km 산출 알고리즘: **§10-9**.

### 9-1. 행안부 인구감소지수와의 관계 (준용 재정의)

행안부 인구감소지수는 **8개 지표 항목**과 가중치 체계를 공표하지만, **개별 정규화 공식·가중치 수치 원문은 비공개**(한국지방행정연구원 용역 보고서 수준)입니다. TownPulse는 다음을 명시합니다.

| 구분 | TownPulse MVP |
|---|---|
| 지표 **항목** | 행안부 8개 중 ①②③⑤⑥을 `pop_decline_score`에 반영. ④⑦은 법정동 공표 없음 → v1.0 REGION(KOSIS #8). ⑧은 `REGION.fiscal_self_reliance` 확보·**MVP 종합 TVI 미반영**(v1.0 보정 검토) |
| 정규화 **방식** | **`pop_decline_score`만** 충북 표본(N≈228) **min-max**. `vacancy_score`·`bus_interval_score`는 §9-4 **절대 선형식**(표본 min-max **아님**) |
| 가중치 **숫자** | MVP **잠정 상수** — 코드·`model_version`에 박음. v1.0 `DelphiModel`에서 숫자만 교체 |

### 9-2. 종합 TVI (최상위 가중합)

```
TVI = pop_decline_score × 0.70
    + vacancy_score     × 0.20
    + bus_interval_score × 0.10
```

| 부분점수 | TVI_SCORE 컬럼 | 범위 | 의미 |
|---|---|---|---|
| `pop_decline_score` | `pop_decline_score` | 0~100 | 인구감소 복합 (§9-3) |
| `vacancy_score` | `vacancy_rate` ★ | 0~100 | 빈집 추정 부분점수 (비율 자체가 아님) |
| `bus_interval_score` | `bus_interval_score` | 0~100 | 배차·정류장 접근성 |

> ★ ERD·DDL 컬럼명 `vacancy_rate`는 **부분점수** 저장용 역사적 명칭 — 실제 빈집 **비율**은 SNAP 교차 계산 중간값.

**위험 등급**

| TVI 점수 | risk_level | label |
|---|---|---|
| 0 ~ 30 | danger | 위험 |
| 31 ~ 60 | warning | 주의 |
| 61 ~ 100 | safe | 안전 |

### 9-3. min-max 정규화 + `pop_decline_score` (5지표 가중합)

`recalculate_all()` **1회차**에 충북 전체 마을(표본 N≈228) SNAP를 스캔해 지표별 `(sample_min, sample_max)`와 §9-5 `prescription_cb_averages`(청년비율·빈집비율 평균)를 계산·메모리 캐시합니다. **추가 테이블·API 없음** — 매월 `collect_all()` 직후 갱신.

```python
# tvi_score_repository.py — private

def normalize(value: float, sample_min: float, sample_max: float, *, invert: bool = False) -> float:
    """0~100. 높을수록 '생존에 유리'. invert=True면 값이 클수록 위험(고령화 등)."""
    if sample_max == sample_min:
        return 50.0
    score = (value - sample_min) / (sample_max - sample_min) * 100.0
    return max(0.0, min(100.0, 100.0 - score if invert else score))


# --- 입력값 (마을 1건) ---
annual_pop_change_rate = (
    (population_total - prev_population_total) / prev_population_total * 100.0
    if prev_population_total else 0.0
)  # 직전 월 SNAP_POPULATION 대비 파생 — 별도 API 없음

population_density = snap_statistics.pop_density          # SNAP_STATISTICS (KOSIS #8)
net_youth_migration = snap_population.net_youth_migration
aging_ratio = (
    snap_population.population_65plus / snap_population.population_total
    if snap_population.population_total else 0.0
)
youth_ratio = (
    snap_population.population_youth / snap_population.population_total
    if snap_population.population_total else 0.0
)  # ★ MVP: API#3의 20~39세 합산 = 청년층 proxy (행안부 ⑥ 유소년 14세 이하와 정의 상이 — 투명 선언)

# --- pop_decline_score (MVP 잠정 가중치 — v1.0 Delphi 교체 대상) ---
POP_DECLINE_WEIGHTS = {
    "annual_pop_change_rate": 0.30,
    "population_density":     0.20,
    "net_youth_migration":    0.25,
    "aging_ratio":            0.15,  # invert=True
    "youth_ratio":            0.10,
}

pop_decline_score = (
    normalize(annual_pop_change_rate, *norms["annual_pop_change_rate"]) * POP_DECLINE_WEIGHTS["annual_pop_change_rate"]
  + normalize(population_density,     *norms["population_density"])     * POP_DECLINE_WEIGHTS["population_density"]
  + normalize(net_youth_migration,    *norms["net_youth_migration"])    * POP_DECLINE_WEIGHTS["net_youth_migration"]
  + normalize(aging_ratio,            *norms["aging_ratio"], invert=True) * POP_DECLINE_WEIGHTS["aging_ratio"]
  + normalize(youth_ratio,            *norms["youth_ratio"])            * POP_DECLINE_WEIGHTS["youth_ratio"]
)
```

| 행안부 지표 | SNAP/파생 필드 | `pop_decline_score` 반영 |
|---|---|---|
| ① 연평균인구증감률 | `annual_pop_change_rate` (전월 대비 파생) | ✅ |
| ② 인구밀도 | `SNAP_STATISTICS.pop_density` | ✅ |
| ③ 청년순이동률 | `SNAP_POPULATION.net_youth_migration` | ✅ |
| ⑤ 고령화비율 | `population_65plus / population_total` | ✅ (invert) |
| ⑥ 유소년비율 | `population_youth / population_total` (청년 proxy) | ✅ |
| ④ 주간인구 | `REGION.daytime_population` | ❌ MVP — v1.0 |
| ⑦ 조출생률 | `REGION.birth_rate` | ❌ MVP — v1.0 |
| ⑧ 재정자립도 | `REGION.fiscal_self_reliance` | ❌ MVP 종합 TVI — v1.0 |

### 9-3-1. 상대평가 한계·`tvi_delta` 해석 ★ v9.3

> MVP는 §9-3 **월간 raw min/max 즉시 교체** 상대평가를 유지합니다. 완만화(EMA)·기준점 고정은 **v1.0** — `TownPulse_백엔드_MVP이후_개발정의서_v4_0.md` §1-1.

**왜곡 메커니즘**

- `pop_decline_score`(TVI 70%)는 매 `finalize_monthly_snap()` → `recalculate_all()` 때 충북 N≈228 표본의 **그 달 raw** `(sample_min, sample_max)`로 정규화됩니다.
- 마을 **raw 지표**가 개선되어도, 다른 읍면동 극단값 변화만으로 해당 마을의 정규화 점수·종합 TVI·`risk_level`이 **하락**할 수 있습니다.
- `tvi_delta`는 **종합 TVI 점수의 전월 대비 차분**입니다. 잣대(min/max)가 월마다 바뀌면 delta에 **표본 잣대 변화**가 섞입니다.

```python
# tvi_score_repository.recalculate_all() — 마을별 upsert 시
prev = await self._find_previous_month_score(village_id)
tvi_delta = round(tvi_total - prev.tvi_score, 2) if prev else 0.0
```

| 질문 (지자체) | MVP 대응 |
|---|---|
| "지표는 좋아졌는데 점수는 왜 떨어졌나?" | TVI는 **충북 내 상대순위** — §9-3-1 왜곡 설명 + **raw 5지표 전월 대비** 별도 표시 권장 (프론트 D-04, 사업정의서 §7-6) |
| "전월 대비 몇 점 올랐나?" | `tvi_delta` 참고 — **잣대 효과 포함** 가능, 단독 설득 근거로 쓰지 말 것 |

**MVP 구현 범위:** 본 절 **문서·UI 카피** 확정. `tvi_norm_state` 테이블·EMA 코드는 **구현하지 않음** (해커톤 전 1~2회 배치에서는 완만화 체감도 없음).

### 9-4. `vacancy_score` · `bus_interval_score` (선형식 — min-max **미적용**) ★ v8.8 → v9.4

> §9-3 `normalize()`는 **`pop_decline_score` 전용**. 빈집·교통은 아래 고정 선형 변환만 사용합니다.  
> ★ **v9.4:** `bus_route_count is None`(`tago_city_code` 미보유, 증평군) = 노선 데이터 **미보유**이지 교통 공백 **확정**이 아님 — `calculate_bus_interval_score()` 3단계 분기.

```python
# SNAP_BUILDING × SNAP_POPULATION — registered_households는 SNAP_POPULATION 소속 (§5-3②)
vacancy_estimated = max(0, residential_buildings - registered_households)
vacancy_ratio = vacancy_estimated / residential_buildings if residential_buildings else 0.0
vacancy_score = max(0.0, 100.0 - vacancy_ratio * 200.0)  # → TVI_SCORE.vacancy_rate 컬럼에 저장

# SNAP_TRANSPORT — 정류장 접근성 + 배차 (v8.3 → v9.4)
def calculate_bus_interval_score(
    bus_route_count: int | None,
    avg_bus_interval_min: float | None,
    nearest_stop_distance_m: int | None,
    bus_stops_within_1km: int,
) -> float:
    """bus_route_count=None → TAGO 노선 미보유(증평군). 0 강제 대신 보수적 절충."""
    has_route_data = bus_route_count is not None

    if bus_stops_within_1km == 0 or (
        nearest_stop_distance_m is not None and nearest_stop_distance_m > 1000
    ):
        if not has_route_data:
            return 30.0  # MVP 잠정 — 500m만 실측·1km 미확인 (v1.0 Delphi)
        return 0.0  # 노선 카탈로그까지 확인된 확정 교통 공백

    if avg_bus_interval_min:
        return max(0.0, 100.0 - (avg_bus_interval_min / 2.0))

    if not has_route_data:
        return 50.0  # 정류장 실측 OK·배차 미상 — 중립 잠정값

    return 0.0
```

> `30.0`/`50.0`은 통계적 실측 근거가 아닌 **MVP 잠정 절충값** — "0(확정 공백)보다는 낫고 정상 배차 점수라 단정하기 어렵다"는 보수 추정. v1.0 `TVI_MODEL_VERSION`·Delphi 재검토.

### 9-5. 처방 TVI 기대치 — `simulate_tvi_gain()` (역산, 별도 근거표 없음) ★ v9.5

TVI는 결정론적 가중합이므로 **처방 후 기대 TVI = §9 공식에 "처방이 바꾼 SNAP"을 넣어 재계산**한 Δ입니다. `tvi_gain_min`/`tvi_gain_max`는 단가 라이브러리 범위를 `intensity_min`/`intensity_max`로 대입한 결과입니다.

> ★ **v9.5:** `INCENTIVE`·`SOC_COMPLEX`의 `예산 → SNAP` 환산은 **기존 적재 SNAP·충북 표본 평균**을 연동한 **잠정 계수**입니다. 실증 인과관계가 아니며, ΔTVI는 §9 역산으로 추적 가능합니다. 재정자립도 분할 표기·단가 각주 UI·Delphi/ML 계수 정식화는 **MVP이후 v4_0** §1-6.

**표본 평균 (`recalculate_all()` 1회차 스캔, min-max와 동일 패턴)**

```python
@dataclass
class PrescriptionCbAverages:
    youth_ratio_avg: float           # population_youth / population_total 평균
    vacant_house_rate_avg: float     # §9-4 vacancy_ratio 평균

# tvi_score_repository.recalculate_all() — N≈228 스캔 후 norms에 부착
# simulate_tvi_gain()은 **동일 norms** 사용 (메모리 캐시만 가정 금지)
```

```python
# prescription_result_repository.py — private

def calculate_tvi(snap_bundle: VillageSnapBundle, norms: TviNorms) -> float:
    """§9-2~9-4 단일 진입점 — recalculate_all()과 처방 시뮬레이션 **동일 함수**."""

def simulate_tvi_gain(
    snap_before: VillageSnapBundle,
    prescription_code: str,
    budget_min: int,
    budget_max: int,
    norms: TviNorms,
) -> tuple[float, float]:
    tvi_before = calculate_tvi(snap_before, norms)
    gains = []
    for budget in (budget_min, budget_max):
        snap_after = apply_prescription_effect(snap_before, prescription_code, budget, norms)
        gains.append(calculate_tvi(snap_after, norms) - tvi_before)
    return (min(gains), max(gains))
```

**INCENTIVE — 동적 정착률 γ (v9.5)**

```
M = (예산 ÷ 가구당 단가) × γ
γ = SETTLEMENT_RATE_BASE × f_transport × f_youth_ratio
SETTLEMENT_RATE_BASE = 0.30   # 행안부 기금 사례 보수 추정 — 잠정
```

```python
SETTLEMENT_RATE_BASE = 0.30

def _confirmed_transport_gap(st: SnapTransport) -> bool:
    """§9-4·v9.4 — 노선 데이터 있을 때만 확정 공백."""
    if st.bus_route_count is None:
        return False
    return st.bus_stops_within_1km == 0 or (
        st.nearest_stop_distance_m is not None and st.nearest_stop_distance_m > 1000
    )

def f_transport(st: SnapTransport) -> float:
    if _confirmed_transport_gap(st):
        return 0.70   # 인프라 한계 — 정착률 보수 하향
    if st.bus_route_count is None:
        return 1.00   # 증평형 TAGO 미보유 — 중립
    if st.bus_stops_within_1km > 0 and (
        st.nearest_stop_distance_m is None or st.nearest_stop_distance_m <= 1000
    ):
        return 1.20   # 정류장 접근 양호
    return 1.00

def f_youth_ratio(youth_ratio: float, cb_avg: float) -> float:
    if cb_avg <= 0:
        return 1.0
    return max(0.8, min(1.2, youth_ratio / cb_avg))

def incentive_settlement_rate(snap: VillageSnapBundle, norms: TviNorms) -> float:
    youth_ratio = snap.population.population_youth / max(snap.population.population_total, 1)
    cb = norms.prescription_cb_averages
    return SETTLEMENT_RATE_BASE * f_transport(snap.transport) * f_youth_ratio(
        youth_ratio, cb.youth_ratio_avg
    )
```

**SOC_COMPLEX — 빈집 비율 연계 (v9.5)**

```
pop_density_new = pop_density_old × (1 + SOC_DENSITY_BASE_DELTA × vacant_house_rate / vacant_house_rate_cb_avg)
SOC_DENSITY_BASE_DELTA = 0.05
```

```python
SOC_DENSITY_BASE_DELTA = 0.05

def vacancy_ratio(snap: VillageSnapBundle) -> float:
  """§9-4와 동일 중간값."""
  rb = snap.building.residential_buildings
  if not rb:
      return 0.0
  vac = max(0, rb - snap.population.registered_households)
  return vac / rb

def soc_complex_density_factor(snap: VillageSnapBundle, norms: TviNorms) -> float:
    vr = vacancy_ratio(snap)
    cb_avg = norms.prescription_cb_averages.vacant_house_rate_avg
    if cb_avg <= 0:
        return 1.0 + SOC_DENSITY_BASE_DELTA
    return 1.0 + SOC_DENSITY_BASE_DELTA * (vr / cb_avg)
```

**처방별 SNAP 변경 규칙 (MVP 5종)**

| 코드 | 변경 SNAP 필드 | 변경량 산출 | 잠정 가정 |
|---|---|---|---|
| `VAC_BUY` | `residential_buildings` 유지, `registered_households` += N | N = 예산 ÷ `BUDGET_UNIT_PRICE` (채당) | 매입 즉시 거주 전환 |
| `VAC_REMODEL` | `registered_households` += N | N = 예산 ÷ 채당 단가 | 귀농 임대 1세대=1세대 |
| `DRT` | `avg_bus_interval_min` 감소 **만** | 목표 배차 = `PRESCRIPTION_TYPE.meta_target_interval_min` (시드 30분) | **확정 교통 공백**만 배차 단축해도 §9-4 `0.0` 유지. `bus_route_count=None`(증평형)은 절충값 |
| `INCENTIVE` | `net_youth_migration` += M | M = (예산 ÷ 가구당 단가) × **γ** (`incentive_settlement_rate`) | γ = 0.30 × 교통 × 청년비율 보정 — **SNAP 연동 잠정** ★ v9.5 |
| `SOC_COMPLEX` | `pop_density` 소폭 ↑ | `× soc_complex_density_factor()` | 빈집 비율↑ → 복합화 효과 가중 — **잠정** ★ v9.5 |

> **한계 선언**: `0.30`·`0.70`/`1.20`·`0.05`·clamp 구간은 **Delphi·실증 ML 이전의 잠정 계수**입니다. `PRESCRIPTION_TYPE` 메타·`model_version`에 명시. TVI Δ는 §9 역산 **100% 추적**. Gemini는 Δ 숫자를 생성하지 않음 — **§11-1b**.

---

## 10. 공공데이터 배치 수집 (Repository + PUBLIC_DATA_SYNC_ORCHESTRATOR) ★ v8.1

> ★ v8.3 SNAP_TRANSPORT = #6 + **15098534** (마을 ingest). ★ v8.2 API **8종**. ★ v8: pipeline 삭제 → `{table}_repository.py`. ★ v8.1: PUBLIC_DATA_SYNC_ORCHESTRATOR 12파일.

### 10-1. 호출 흐름

```
[자동 — APScheduler]
main.py lifespan
  → build_public_data_sync_interactor()   # Provider 팩토리 — Depends 없이 cron 전용
  → register_batch_jobs(interactor)
  → scheduler.start()

APScheduler ① — 매월 1일 03:00 KST
  → public_data_sync_orchestrator_interactor.collect_all()
       → public_data_sync_orchestrator_port.save_job_started(...)   # 이력 시작
       → for village: village_port.update_geocode_from_vworld(...)  # API#7 ★ 선행
       → region_port.find_all_legal_dong_codes()
       → for code: snap_population/building/statistics ingest      # API#1~4·8
       → for village: snap_transport_port.ingest_for_village(...)  # API#6 + 15098534 ★ v8.3
       → tvi_score_port.recalculate_all()                           # §9
       → public_data_sync_orchestrator_port.save_job_completed(...) # 이력 완료

APScheduler ② — 매년 1월 1일 04:00 KST
  → public_data_sync_orchestrator_interactor.ingest_fiscal_all()
       → region_port.ingest_fiscal_self_reliance()                  # API#5

[수동 — HTTP (운영·심사)]
POST /api/townpulse/admin/sync/trigger
  → Router → mapper → PublicDataSyncOrchestratorUseCase.trigger_sync()
  → Interactor (동일 collect_all / ingest_fiscal_all 경로)

★ 배치·수동 모두 Router → Interactor → Port → Repository — matrix collector·Repository 직접 호출 **금지**
★ 공공API fetch·TVI 산식은 여전히 각 `{table}_repository.py` **private** (SRP 유지)
```

### 10-2. PUBLIC_DATA_SYNC_ORCHESTRATOR — 12파일 프랙탈 ★ v8.1

| # | 레이어 | 파일 | 책임 |
|---|---|---|---|
| 1 | Entity | `public_data_sync_orchestrator_entity.py` | `PublicDataSyncJobEntity` — job_id, job_type, status, started_at, finished_at, error_message, processed_count |
| 2 | Input Port | `public_data_sync_orchestrator_use_case.py` | `collect_all`, `ingest_fiscal_all`, `trigger_sync`, `get_latest_job`, `get_job_by_id` |
| 3 | Output Port | `public_data_sync_orchestrator_port.py` | 동기화 **이력** persist·조회 (NeonDB) |
| 4 | Interactor | `public_data_sync_orchestrator_interactor.py` | Morpheus 상속, **타 도메인 Output Port 7개** 주입으로 ingest 조율 (Repository 직접 금지) |
| 5 | DTO | `public_data_sync_orchestrator_dto.py` | `SyncTriggerCommandDto`, `SyncJobResultDto`, `SyncJobQueryDto` |
| 6 | Router | `public_data_sync_orchestrator_router.py` | `POST /admin/sync/trigger`, `GET /admin/sync/jobs/latest`, `GET /admin/sync/jobs/{job_id}` |
| 7 | Schema | `public_data_sync_orchestrator_schema.py` | 요청·응답 Pydantic |
| 8 | Inbound Mapper | `public_data_sync_orchestrator_mapper.py` | Schema ↔ DTO |
| 9 | ORM | `public_data_sync_orchestrator_orm.py` | `public_data_sync_job` 테이블 (오케스트레이터 전용 이력 — ERD 18 테이블 외) |
| 10 | ORM Mapper | `public_data_sync_orchestrator_orm_mapper.py` | ORM ↔ Entity |
| 11 | Repository | `public_data_sync_orchestrator_repository.py` | 이력 CRUD + `find_all_legal_dong_codes()`는 **region_port 위임** (교차 read 최소화) |
| 12 | Provider | `public_data_sync_orchestrator_provider.py` | Interactor 조립 + **APScheduler·register_batch_jobs·scheduler** export |

> **Output Port 7개 주입 (Provider Depends 체이닝):** `RegionPort`, `VillagePort`, `SnapPopulationPort`, `SnapBuildingPort`, `SnapTransportPort`, `SnapStatisticsPort`, `TviScorePort` — 각 Port에 batch 메서드(`ingest_*`, `recalculate_all`) 선언.

> **Morpheus:** 4번째 오케스트레이터도 `grid_morpheus_base_orchestrator.py` 상속. `collect_all`은 공공API rate limit 때문에 **순차 루프** (gather 병렬 ingest 금지). 이력 조회·상태 VO 판정 등 보조 로직만 Morpheus 패턴 공유.

### 10-3. VO AOP — 배치 동기화 ★ v8.1

| VO | 파일 | 용도 |
|---|---|---|
| `SyncJobTypeVo` | `sync_job_type_vo.py` | `MONTHLY_SNAP` \| `FISCAL_YEARLY` — cron·수동 트리거 공통 |
| `SyncJobStatusVo` | `sync_job_status_vo.py` | `PENDING` \| `RUNNING` \| `COMPLETED` \| `FAILED` — Entity·DTO 상태 판정 |

> 기존 `village_code_vo.py`는 geocode 루프에서 village 식별 시 재사용. VO는 `domain/value_objects/` AOP 배치 — 프랙탈 미적용.

### 10-4. 타 도메인 Output Port — batch 메서드 (발췌)

```python
# app/ports/output/snap_population_port.py (발췌 — SNAP_* 4종 동일 패턴)
class SnapPopulationPort(ABC):
    ...
    @abstractmethod
    async def ingest_from_public_api(self, legal_dong_code: str) -> None: ...

# app/ports/output/region_port.py (발췌)
class RegionPort(ABC):
    ...
    @abstractmethod
    async def find_all_legal_dong_codes(self) -> list[str]: ...
    @abstractmethod
    async def ingest_fiscal_self_reliance(self) -> None: ...
    @abstractmethod
    async def ingest_kosis_sigungu_demographics(self) -> None: ...  # v1.0 ★ v8.4

# app/ports/output/village_port.py (발췌)
class VillagePort(ABC):
    ...
    @abstractmethod
    async def find_by_id(self, village_id: str) -> VillageEntity | None: ...  # ★ v8.6
    @abstractmethod
    async def find_all_for_geocode_sync(self) -> list[VillageEntity]: ...
    @abstractmethod
    async def update_geocode_from_vworld(self, village_id: UUID) -> None: ...

# app/ports/output/tvi_score_port.py (발췌)
class TviScorePort(ABC):
    ...
    @abstractmethod
    async def find_by_id(self, tvi_score_id: str) -> TviScoreEntity | None: ...  # ★ v8.6
    @abstractmethod
    async def recalculate_all(self) -> None: ...
```

### 10-5. Repository ↔ API 매핑 (ingest 구현 위치)

| Repository / Port | batch 메서드 | API | write |
|---|---|---|---|
| `snap_population_repository` | `ingest_core_from_public_api()` / `ingest_migration_from_public_api()` | #2+#3 / #4 | SNAP_POPULATION |
| `snap_building_repository` | `ingest_from_public_api()` | #1 | SNAP_BUILDING |
| `snap_transport_repository` | `ingest_for_village()` | #6 + **15098534** | SNAP_TRANSPORT |
| `snap_statistics_repository` | `ingest_from_public_api()` | #8 | SNAP_STATISTICS |
| `village_repository` | `update_geocode_from_vworld()` | #7 | VILLAGE |
| `region_repository` | `ingest_fiscal_self_reliance()` | #5 | REGION |
| `region_repository` | `ingest_kosis_sigungu_demographics()` | #8 (시군구) | REGION (`birth_rate` 등, v1.0) ★ v8.4 |
| `tvi_score_repository` | `recalculate_all()` | SNAP read | TVI_SCORE |

### 10-6. Provider — APScheduler + Interactor 조립 ★ v8.1

```python
# dependencies/public_data_sync_orchestrator_provider.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.matrix.grid_oracle_database_manager import get_db
from townpulse.app.use_cases.public_data_sync_orchestrator_interactor import (
    PublicDataSyncOrchestratorInteractor,
)
# ... RegionPort, VillagePort, Snap*Port, TviScorePort provider import

scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

async def get_public_data_sync_orchestrator_use_case(
    db: AsyncSession = Depends(get_db),
    region_port: RegionPort = Depends(get_region_port),
    village_port: VillagePort = Depends(get_village_port),
    snap_population_port: SnapPopulationPort = Depends(get_snap_population_port),
    snap_building_port: SnapBuildingPort = Depends(get_snap_building_port),
    snap_transport_port: SnapTransportPort = Depends(get_snap_transport_port),
    snap_statistics_port: SnapStatisticsPort = Depends(get_snap_statistics_port),
    tvi_score_port: TviScorePort = Depends(get_tvi_score_port),
    sync_port: PublicDataSyncOrchestratorPort = Depends(get_public_data_sync_orchestrator_port),
) -> PublicDataSyncOrchestratorUseCase:
    return PublicDataSyncOrchestratorInteractor(
        sync_port=sync_port,
        region_port=region_port,
        village_port=village_port,
        snap_population_port=snap_population_port,
        snap_building_port=snap_building_port,
        snap_transport_port=snap_transport_port,
        snap_statistics_port=snap_statistics_port,
        tvi_score_port=tvi_score_port,
    )

def register_batch_jobs(interactor: PublicDataSyncOrchestratorUseCase) -> None:
    scheduler.add_job(interactor.collect_all, "cron", day=1, hour=3, id="snap_monthly")
    scheduler.add_job(
        interactor.ingest_fiscal_all, "cron", month=1, day=1, hour=4, id="region_fiscal_yearly"
    )
    # v1.0: scheduler.add_job(interactor.ingest_kosis_demographics_all, "cron", month=1, day=2, hour=5, ...)

async def build_public_data_sync_interactor() -> PublicDataSyncOrchestratorUseCase:
    """lifespan·cron 전용 — HTTP Depends 없이 Port·Repository 직접 조립."""
    async with get_oracle_session_factory() as session:
        return PublicDataSyncOrchestratorInteractor(
            sync_port=PublicDataSyncOrchestratorRepository(session=session),
            region_port=RegionRepository(session=session),
            village_port=VillageRepository(session=session),
            snap_population_port=SnapPopulationRepository(session=session),
            snap_building_port=SnapBuildingRepository(session=session),
            snap_transport_port=SnapTransportRepository(session=session),
            snap_statistics_port=SnapStatisticsRepository(session=session),
            tvi_score_port=TviScoreRepository(session=session),
        )
```

### 10-7. Interactor — 월간 배치 3단계 (발췌) ★ v9.0

개발계정 **10,000회/일** 한도 때문에 API#4(`net_youth_migration`) 7,752회를 **같은 날** population·building·transport와 한꺼번에 돌리지 않습니다. **3단계 분할** — SSOT: §10-8-1-5.

**MVP 제출 일정 (2026-06-26 제출 · freeze 06-25):**

| 일자 | 실행 | 비고 |
|---|---|---|
| 06-23 | `collect_all_core()` | vworld·pop#2#3·building·transport·statistics |
| 06-23~25 | `collect_migration_chunk(0)` → `(1)` → `(2)` | 법정동 76개×34회≈2,584회/일 |
| 06-25 PM | `finalize_monthly_snap()` | `recalculate_all()` — `net_youth_migration` 포함 TVI |

```python
# app/use_cases/public_data_sync_orchestrator_interactor.py
from domain.value_objects.sync_job_type_vo import SyncJobTypeVo
from domain.value_objects.sync_job_status_vo import SyncJobStatusVo

MIGRATION_CHUNKS = 3  # 228 ÷ 3 = 76 법정동/chunk


class PublicDataSyncOrchestratorInteractor(MorpheusOrchestratorBase):
    async def collect_all_core(self) -> SyncJobResultDto:
        """Phase A — API#4 제외. migration_chunk 없이 핵심 SNAP 적재."""
        job = await self._sync_port.save_job_started(
            SyncJobTypeVo.MONTHLY_SNAP, meta={"phase": "core"}
        )
        try:
            villages = await self._village_port.find_all_for_geocode_sync()
            for village in villages:
                await self._village_port.update_geocode_from_vworld(village.id)
            codes = await self._region_port.find_all_legal_dong_codes()
            for code in codes:
                await self._snap_population_port.ingest_core_from_public_api(code)  # API#2+#3만
                await self._snap_building_port.ingest_from_public_api(code)
                await self._snap_statistics_port.ingest_from_public_api(code)
            for village in villages:
                await self._snap_transport_port.ingest_for_village(village.id)
            return await self._sync_port.save_job_completed(job.id, SyncJobStatusVo.COMPLETED)
        except Exception as exc:
            await self._sync_port.save_job_failed(job.id, str(exc))
            raise

    async def collect_migration_chunk(self, chunk_index: int) -> SyncJobResultDto:
        """Phase B — API#4 net_youth_migration만. chunk_index 0|1|2."""
        if chunk_index not in range(MIGRATION_CHUNKS):
            raise ValueError("chunk_index must be 0, 1, or 2")
        job = await self._sync_port.save_job_started(
            SyncJobTypeVo.MONTHLY_SNAP, meta={"phase": "migration", "chunk": chunk_index}
        )
        try:
            codes = await self._region_port.find_all_legal_dong_codes()
            chunk = self._split_legal_dong_chunk(codes, MIGRATION_CHUNKS, chunk_index)
            for code in chunk:
                await self._snap_population_port.ingest_migration_from_public_api(code)
            return await self._sync_port.save_job_completed(job.id, SyncJobStatusVo.COMPLETED)
        except Exception as exc:
            await self._sync_port.save_job_failed(job.id, str(exc))
            raise

    async def finalize_monthly_snap(self) -> SyncJobResultDto:
        """Phase C — migration 3chunk 완료 후 TVI 재계산."""
        job = await self._sync_port.save_job_started(
            SyncJobTypeVo.MONTHLY_SNAP, meta={"phase": "finalize"}
        )
        try:
            await self._tvi_score_port.recalculate_all()
            return await self._sync_port.save_job_completed(job.id, SyncJobStatusVo.COMPLETED)
        except Exception as exc:
            await self._sync_port.save_job_failed(job.id, str(exc))
            raise

    @staticmethod
    def _split_legal_dong_chunk(codes: list[str], n: int, i: int) -> list[str]:
        size = (len(codes) + n - 1) // n
        return codes[i * size : (i + 1) * size]

    async def collect_all(self) -> SyncJobResultDto:
        """하위 호환 — Phase A만 실행. 운영 cron은 core→migration×3→finalize 순차."""
        return await self.collect_all_core()

    async def ingest_fiscal_all(self) -> SyncJobResultDto:
        job = await self._sync_port.save_job_started(SyncJobTypeVo.FISCAL_YEARLY)
        await self._region_port.ingest_fiscal_self_reliance()
        return await self._sync_port.save_job_completed(job.id, SyncJobStatusVo.COMPLETED)
```

> **운영 cron (MVP 이후):** 매월 1일 03:00 `collect_all_core` → 1~3일 04:00 `collect_migration_chunk(0..2)` → 3일 06:00 `finalize_monthly_snap`. 수동 트리거도 동일 4 endpoint.

### 10-8. snap_population_repository (발췌) ★ v9.0

#### 10-8-1. API#4 `net_youth_migration` 집계

##### 10-8-1-1. API 구조 (probe 근거)

행안부 `ppltnDataStus/selectPpltnDataStus`(15108093)는 `mvinAdmmCd`(전입지)·`mvtAdmmCd`(전출지) **둘 다 필수** — **(전입지, 전출지) 한 쌍**당 만 N세(0~110+) 이동 인구 1건. API#3처럼 법정동 하나만 넣어 전체가 나오지 않음 → **상대 행정코드 스윕** 필요.

##### 10-8-1-2. `mvinAdmmCd` 해석 — `legal_dong_code` 직접 사용 금지

| 코드 | 예시 (probe) | 용도 |
|---|---|---|
| `legal_dong_code` / `stdgCd` | `4311110100` (영동) | API#2·#3·SNAP 조인키 |
| `mvinAdmmCd` / `admmCd` | `4311152500` (중앙동) | **API#4 전용** 행정기관코드 |

해석 순서 (`_resolve_mvin_admm_cd`):

1. `REGION.emd_code` (시드·nullable)
2. API#2 응답 `admmCd` 최빈값 (`stdgCd=legal_dong_code` 행)
3. 실패 → `logger.warning("admm_cd_unresolved")` + 해당 법정동 migration **스킵** (`net_youth_migration=NULL` 유지)

##### 10-8-1-3. 시/도 17개 스윕 (채택)

| | 시군구 스윕 | **시/도 스윕 (채택)** |
|---|---|---|
| 호출/법정동 | ~500회 | **34회** (17×2) |
| 월간 228동 | 114,000회 ❌ | **7,752회** |
| net 정밀도 | — | **손실 없음** (출신 breakdown 미사용) |

`net_youth_migration = Σ(17시도→이동, 청년 20~39) − Σ(이동→17시도, 청년 20~39)`

probe: `.env.local` `PROBE_MVT_ADMM_CD=1100000000`(서울 시도 단위) ✅ · `15108093_migration.json`은 동 단위 `1168070000` 샘플(정밀도 참고용).

##### 10-8-1-4. VO + Repository

```python
# domain/value_objects/sido_code_vo.py
SIDO_CODES: dict[str, str] = {
    "11": "서울특별시", "26": "부산광역시", "27": "대구광역시", "28": "인천광역시",
    "29": "광주광역시", "30": "대전광역시", "31": "울산광역시", "36": "세종특별자치시",
    "41": "경기도", "42": "강원특별자치도", "43": "충청북도", "44": "충청남도",
    "45": "전북특별자치도", "46": "전라남도", "47": "경상북도", "48": "경상남도",
    "50": "제주특별자치도",
}

def sido_admm_cd(sido_code: str) -> str:
    return f"{sido_code}00000000"


# adapter/outbound/repositories/snap_population_repository.py
YOUTH_AGES = range(20, 40)  # §9-3 youth_ratio·API필드검증과 동일


def _sum_youth_count(item: dict) -> int:
    return sum(
        int(item.get(f"male{age}AgeNmprCnt") or 0) + int(item.get(f"feml{age}AgeNmprCnt") or 0)
        for age in YOUTH_AGES
    )


class SnapPopulationRepository(SnapPopulationPort):
    async def ingest_core_from_public_api(self, legal_dong_code: str) -> None:
        """API#2+#3 — migration 제외 (Phase A)."""
        raw = await self._fetch_mois_household_age(legal_dong_code)
        await self._upsert_snap_row(legal_dong_code, raw)

    async def ingest_migration_from_public_api(self, legal_dong_code: str) -> None:
        """API#4만 — Phase B chunk."""
        admm_cd = await self._resolve_mvin_admm_cd(legal_dong_code)
        if not admm_cd:
            return
        ym = self._current_stats_ym()
        net_youth = await self._compute_net_youth_migration(admm_cd, ym)
        await self._upsert_snap_row(legal_dong_code, {"net_youth_migration": net_youth})

    async def _resolve_mvin_admm_cd(self, legal_dong_code: str) -> str | None:
        region = await self._region_port.find_by_legal_dong_code(legal_dong_code)
        if region and region.emd_code:
            return region.emd_code
        rows = await self._fetch_mois_household_rows(legal_dong_code)
        from collections import Counter
        counts = Counter(r["admmCd"] for r in rows if r.get("admmCd"))
        return counts.most_common(1)[0][0] if counts else None

    async def _fetch_migration_pair(
        self, mvin_admm_cd: str, mvt_admm_cd: str, stats_ym: str
    ) -> dict:
        body = await self._call_ppltn_data_stus(
            mvinAdmmCd=mvin_admm_cd,
            mvtAdmmCd=mvt_admm_cd,
            srchFrYm=stats_ym,
            srchToYm=stats_ym,
            lv="3",
        )
        return body["Response"]["items"]["item"]  # totalCount=1, 페이징 불필요

    async def _compute_net_youth_migration(self, admm_cd: str, stats_ym: str) -> int:
        total_in = 0
        for sido in SIDO_CODES:
            raw = await self._fetch_migration_pair(admm_cd, sido_admm_cd(sido), stats_ym)
            total_in += _sum_youth_count(raw)
        total_out = 0
        for sido in SIDO_CODES:
            raw = await self._fetch_migration_pair(sido_admm_cd(sido), admm_cd, stats_ym)
            total_out += _sum_youth_count(raw)
        return total_in - total_out
```

##### 10-8-1-5. API 호출량·3일 분할

| Phase | 호출/월 (추정) | 호출/일 |
|---|---|---|
| A `collect_all_core` (pop#2#3·building·transport·stats) | ~5,000~7,000 | 1일 |
| B `collect_migration_chunk` ×3 | 7,752 | **~2,584/일** |
| C `finalize_monthly_snap` | 0 (DB only) | 1일 |

**합계:** 한도 10,000/일 준수 — **A와 B를 같은 날 돌리지 않음** (MVP: 6/23 A → 6/23~25 B → 6/25 C).

### 10-8b. snap_building_repository — `mainPurpsCdNm` 화이트리스트 (발췌) ★ v8.10

#### 10-8b-1. 판정 사전 (건축법 시행령 별표1)

원칙: 별표1 표준 용도분류에 없는 키워드는 사전에 추가하지 않음. fuzzy/substring 매칭 금지 — **정확매칭만**.

| `mainPurpsCdNm` | 별표1 분류 | 화이트리스트 | 근거/사유 |
|---|---|---|---|
| 단독주택 | 제1호 가목 | ✅ | |
| 다중주택 | 제1호 나목 | ✅ **신규** | 단독주택 하위 — 기존 6종 목록 누락분 |
| 다가구주택 | 제1호 다목 | ✅ | |
| 공관 | 제1호 라목 | ❌ 제외 | 공공기관장 관저 — 일반 주거 빈집 통계 대상 아님 |
| 공동주택 | 제2호 (총칭) | ✅ | API가 세부분류 대신 총칭 반환 시 |
| 아파트 | 제2호 가목 | ✅ | |
| 연립주택 | 제2호 나목 | ✅ | |
| 다세대주택 | 제2호 다목 | ✅ | |
| **기숙사** | 제2호 라목 | ❌ **제외 (확정)** | 법적으론 공동주택 하위이나 학교·공장 부속 성격 — 마을 빈집 비율 왜곡. v1.0 별도 컬럼 검토 |
| 오피스텔 | 제14호 나목2 (업무시설) | ❌ 제외 | 업무시설 — 의도적 제외 |
| NULL / 빈 문자열 / 표준 외 값 | — | ❌ + **unmatched 로그** | 무음 제외 금지 — ingest 시 빈도 집계 |

> **"농가창고 겸용 주택" 등 서술형 표현:** 별표1 표준 목록에 없음 — probe로 실측 확인 전 사전 미추가. 주 건물은 `단독주택`·부속 시설은 별도 동(棟) 레코드일 가능성이 큼 (`building_hub_title.json` 10건 샘플에는 미출현).

#### 10-8b-2. VO + 감사 로깅

```python
# domain/value_objects/residential_purpose_vo.py
# 별표1 제1호(단독주택)·제2호(공동주택) 근거. 공관·기숙사·오피스텔은 §10-8b-1 의도적 제외.
RESIDENTIAL_PURPOSE_NAMES: frozenset[str] = frozenset({
    "단독주택", "다중주택", "다가구주택",
    "공동주택", "아파트", "연립주택", "다세대주택",
})


def is_residential(main_purps_nm: str | None) -> bool:
    if not main_purps_nm:
        return False
    return main_purps_nm.strip() in RESIDENTIAL_PURPOSE_NAMES
```

```python
# adapter/outbound/repositories/snap_building_repository.py
from domain.value_objects.residential_purpose_vo import RESIDENTIAL_PURPOSE_NAMES

class SnapBuildingRepository(SnapBuildingPort):
    async def _count_residential_with_audit(
        self, rows: list[dict]
    ) -> tuple[int, dict[str, int]]:
        count = 0
        unmatched: dict[str, int] = {}
        for r in rows:
            raw = (r.get("mainPurpsCdNm") or "").strip()
            if raw in RESIDENTIAL_PURPOSE_NAMES:
                count += 1
            elif raw:
                unmatched[raw] = unmatched.get(raw, 0) + 1
        return count, unmatched

    async def ingest_from_public_api(self, legal_dong_code: str) -> None:
        sigungu_cd = legal_dong_code[:5]
        bjdong_cd = legal_dong_code[5:10]
        rows = await self._fetch_all_br_title_pages(sigungu_cd, bjdong_cd)
        residential_count, unmatched = await self._count_residential_with_audit(rows)
        if unmatched:
            await self._log_unmatched_purpose_names(legal_dong_code, unmatched)
        await self._upsert_snap_row(legal_dong_code, {"residential_buildings": residential_count})

    async def _log_unmatched_purpose_names(
        self, legal_dong_code: str, unmatched: dict[str, int]
    ) -> None:
        """PUBLIC_DATA_SYNC job 로그 또는 sync 실행 로그에 append — 분기별 빈도 검토 후 §10-8b-1 갱신."""
        logger.warning(
            "residential_classification_unmatched",
            extra={"legal_dong_code": legal_dong_code, "values": unmatched},
        )
```

#### 10-8b-3. 운영

1. `collect_all()` ingest 후 `unmatched` 로그를 분기별 빈도순 정렬
2. 빈도 상위 값을 별표1과 대조 — 표준 용도면 §10-8b-1에 근거와 함께 추가
3. 비표준 서술형은 계속 제외 — 법정동당 unmatched ≥5건이면 v1.0에서 `vacancy_rate` 신뢰도 플래그 검토

### 10-9. snap_transport_repository — 노선 + 정류장 1km (발췌) ★ v8.9

#### 10-9-1. API 제약

`BusSttnInfoInqireService/getCrdntPrxmtSttnList` 파라미터: `serviceKey`, `gpsLati`, `gpsLong`, `numOfRows`, `pageNo` — **반경(radius) 없음**. probe 기준 고정 ~500m, `numOfRows`/`pageNo`는 **그 500m 안 페이징**이지 반경 확대가 아님.

→ 1km는 **15098534(500m) + `getRouteAcctoThrghSttnList` 노선 카탈로그**를 `nodeid`로 병합 후 Haversine. **좌표 8방향 스윕(A안) 미채택**. `tago_city_code` NULL(증평군)은 **노선 카탈로그만 생략** — 15098534 GPS 호출은 §10-9-3대로 **유지**.

#### 10-9-2. 채택·비채택

| | A. 좌표 8방향 스윕 | B+C. 노선 카탈로그 + 근접 API (**채택**) |
|---|---|---|
| 1km 커버 | 원 경계 빈틈·마을당 API 8회 | 노선 전 정류장 GPS + 500m 근접 API |
| 배치 비용 | 228×8≈1,824회/월 | 시/군 캐시 + 마을당 15098534 ~1.5회 |
| 의미 | 거리만 | 실제 운행 노선 정류장 + 근접 보강 |

#### 10-9-3. 시/군 캐시 + Haversine ★ v9.4 `city_code`-optional

`collect_all()`은 §10-1대로 `for village: ingest_for_village()` **평탄 루프 유지**. 같은 시/군 마을이 `getRouteNoList`를 반복 호출하지 않도록 **Repository `_city_cache`** (실행당 1회, Provider가 Repository 새로 생성 → 실행 간 누수 없음).

**충북 노선 수 probe (2026-06-21, `town.www/_docs/api_samples/tago_route_counts_chungbuk.json`):**

| 시/군 | `tago_city_code` | 노선 수 |
|---|---|---|
| 청주시 | 33010 | 118 |
| 충주시 | 33020 | 471 |
| 제천시 | 33030 | 268 |
| 보은군 | 33320 | 85 |
| 옥천군 | 33330 | 92 |
| 영동군 | 33340 | 86 |
| 진천군 | 33350 | 110 |
| 괴산군 | 33360 | 173 |
| 음성군 | 33370 | 176 |
| 단양군 | 33380 | 100 |
| **합계** | 10개 시/군 | **1,679** |

**월 1회 `collect_all()` API 호출 추정:**

| operation | 빈도 | 회/월 |
|---|---|---|
| `getRouteNoList` | 시/군당 1 (캐시) | 10 |
| `getRouteInfoIem` | 노선당 1 (캐시) | 1,679 |
| `getRouteAcctoThrghSttnList` | 노선당 1+페이지 (캐시) | ~1,679~2,500 ※ |
| `getCrdntPrxmtSttnList` | 마을당 ~1.5페이지 | ~340 |
| **합계** | | **~3,700~4,500** |

※ 노선당 정류장 수에 따라 페이징 추가 (probe: 1노선 `totalCount` 136 → 2페이지).

```python
# adapter/outbound/repositories/snap_transport_repository.py
import math

def _haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


class SnapTransportRepository(SnapTransportPort):
    def __init__(self, ...) -> None:
        ...
        self._city_cache: dict[str, dict] = {}

    async def _fetch_paginated_items(self, fetch_page, page_size: int = 100) -> list[dict]:
        """totalCount까지 페이지네이션 전수 수집 — 15098534·getRouteAcctoThrghSttnList 공통."""
        first = await fetch_page(page_size, 1)
        items = list(first["items"])
        total = first["totalCount"]
        for page in range(2, math.ceil(total / page_size) + 1):
            items += (await fetch_page(page_size, page))["items"]
        return items

    async def _get_city_transport_data(self, city_code: str) -> dict:
        if city_code in self._city_cache:
            return self._city_cache[city_code]
        route_ids = await self._get_route_no_list(city_code)
        intervals: list[int] = []
        stop_catalog: dict[str, tuple[float, float]] = {}
        for route_id in route_ids:
            detail = await self._get_route_info(city_code, route_id)
            if detail.get("intervaltime"):
                intervals.append(int(detail["intervaltime"]))
            stops = await self._fetch_paginated_items(
                lambda n, p: self._call_route_acct_thrgh_sttn_list(city_code, route_id, n, p)
            )
            for s in stops:
                stop_catalog[s["nodeid"]] = (float(s["gpslati"]), float(s["gpslong"]))
        data = {
            "route_ids": route_ids,
            "avg_interval": sum(intervals) / len(intervals) if intervals else None,
            "stop_catalog": stop_catalog,
        }
        self._city_cache[city_code] = data
        return data

    async def _fetch_all_nearby_stops(self, lat: float, lng: float) -> list[dict]:
        return await self._fetch_paginated_items(
            lambda n, p: self._call_crdnt_prxmt(lat, lng, n, p)
        )

    async def _aggregate_stop_access(
        self, village_lat: float, village_lng: float, city_code: str | None
    ) -> tuple[int | None, int]:
        """15098534(~500m) + (있으면) 노선 카탈로그 병합 → (nearest_stop_distance_m, bus_stops_within_1km).
        ★ v9.4: city_code=None이면 카탈로그 병합 없이 500m 근접 API만 (1km 하한 추정)."""
        near_stops = await self._fetch_all_nearby_stops(village_lat, village_lng)
        catalog: dict[str, tuple[float, float]] = {}
        if city_code:
            catalog = (await self._get_city_transport_data(city_code))["stop_catalog"]
        distances: dict[str, float] = {}
        for s in near_stops:
            distances[s["nodeid"]] = _haversine_m(
                village_lat, village_lng, float(s["gpslati"]), float(s["gpslong"])
            )
        for nodeid, (lat, lng) in catalog.items():
            if nodeid not in distances:
                distances[nodeid] = _haversine_m(village_lat, village_lng, lat, lng)
        if not distances:
            return None, 0
        return round(min(distances.values())), sum(1 for d in distances.values() if d <= 1000)

    async def ingest_for_village(self, village_id: UUID) -> None:
        village = await self._load_village(village_id)  # lat, lng 필수 (API#7 vworld)
        region = await self._region_for_village(village_id)
        city_code = region.tago_city_code
        # ★ v9.4 — city_code 없어도 15098534(GPS) 호출. 즉시 return·0 강제 금지.
        nearest_m, count_1km = await self._aggregate_stop_access(
            village.lat, village.lng, city_code
        )
        if city_code:
            city_data = await self._get_city_transport_data(city_code)
            bus_route_count = len(city_data["route_ids"])
            avg_bus_interval_min = city_data["avg_interval"]
        else:
            bus_route_count = None
            avg_bus_interval_min = None
        await self._upsert_snap_row(village_id, {
            "bus_route_count": bus_route_count,
            "avg_bus_interval_min": avg_bus_interval_min,
            "nearest_stop_distance_m": nearest_m,
            "bus_stops_within_1km": count_1km,
        })
```

> **키:** `BUS_ROUTE_API_KEY` (#6), `BUS_STOP_API_KEY` (15098534 — 통상 동일 인증키).  
> **샘플:** `bus_route_primary.json`, `bus_route_detail.json`, `bus_route_stops.json`, `15098534_stop_nearby.json`, `tago_route_counts_chungbuk.json`.

### 10-10. region_repository — 재정·KOSIS 시군구 (발췌)

```python
# adapter/outbound/repositories/region_repository.py
class RegionRepository(RegionPort):
    async def ingest_fiscal_self_reliance(self) -> None:
        for region in await self._find_all_sigungu():
            value = await self._fetch_fiscal_api(region.sigungu_code)
            await self._update_fiscal_fields(region.id, value)

    async def ingest_kosis_sigungu_demographics(self) -> None:
        """KOSIS #8 — birth_rate, daytime_population. 시군구 단위, v1.0. MVP 미호출."""
        for sigungu in await self._find_distinct_sigungu_codes():
            birth, daytime, year = await self._fetch_kosis_demographics(sigungu)
            await self._update_demographic_fields(sigungu, birth, daytime, year)
```

---
---

## 11. Gemini AI 연동 ★ v7

### 11-1. API 키 마스터 — `core/matrix/grid_keymaker_secret_manager.py`

시스템 전역 API 키·환경 변수·Gemini Client·AI persona 상수를 **Keymaker 싱글톤** 한곳에서 관리합니다.  
`.env.local` 경로: `townpulse-api/.env.local` (`core/matrix/grid_keymaker_secret_manager.py` 기준 3단계 상위).  
Gemini **429 할당량 폴백**은 Smith(`grid_smith_agent_scaler.py`)에 위임합니다.

```python
# core/matrix/grid_keymaker_secret_manager.py
"""시스템 전역 API 키·환경 변수·외부 클라이언트(Gemini 등)를 한곳에서 관리합니다."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.matrix.grid_smith_agent_scaler import (
    DEFAULT_GEMINI_MODEL,
    FALLBACK_GEMINI_MODELS,
    generate_with_fallback,
    models_to_try,
)

TOWNPULSE_PRESCRIPTION_PERSONA = """
당신은 충청북도 지방소멸 대응 정책을 지원하는 AI 행정 전문가입니다.
사용자에게는 이미 시스템이 계산을 마친 TVI(마을생존지수) 데이터와
처방 결과(예산 범위, 기금 출처, 우선순위)가 [데이터] 블록으로 주어집니다.

[절대 규칙 — 위반 금지]
1. [데이터] 블록에 없는 숫자(인구수, 예산, TVI 점수, 퍼센트 등)를
   새로 만들거나 추정하지 마세요. 모든 수치는 주어진 값을 그대로 인용하세요.
2. 예산 범위는 budget_min~budget_max(만원) 그대로만 언급하세요.
   더 정확한 금액을 "추정"하거나 범위를 좁히지 마세요.
3. [데이터]에 없는 기금·법령·사업명을 임의로 언급하지 마세요.
   fund_name/fund_org가 비어 있으면 "기금 매칭 정보 없음"이라고만 안내하세요.
4. 정책 효과를 과장하거나 보장하는 표현("반드시", "확실히 해결됩니다")을
   쓰지 마세요. "~에 기여할 것으로 기대됩니다" 수준으로 서술하세요.

[응답 형식]
다음 4개 섹션을 순서대로, 한국어 행정 보고서 톤으로 작성하세요.
- **요약**: 1~2문장으로 이 처방이 왜 1순위인지
- **실행 방안**: 처방 유형(prescription_type)에 따른 구체적 조치
- **예산 근거**: 주어진 budget_min~budget_max를 그대로 인용, 산출 근거(calculation_note)가 있으면 함께 설명
- **기금 출처**: 주어진 fund_name/fund_org만 안내 (없으면 명시)

[분량 제한]
전체 600자 이내, 마크다운 헤더(#) 사용 금지, 굵게(**)는 섹션 제목에만 사용.
"""


def default_backend_env_path() -> Path:
    """`townpulse-api/.env.local` — 이 파일: `core/matrix/grid_keymaker_secret_manager.py` 기준."""
    return Path(__file__).resolve().parent.parent.parent / ".env.local"


class Keymaker:
    """
    전역 키·설정 관리자.

    - `townpulse-api/.env.local` 로드 (Oracle은 Keymaker 로드 후 os.getenv 사용)
    - Gemini API 키 및 `google.genai.Client` 보관
    - 공공API 8종·JWT 등 `get_secret()`으로 조회
    - `TOWNPULSE_PRESCRIPTION_PERSONA` 상수 보관 (구 shared/ai)
    """

    _instance: Keymaker | None = None

    def __init__(self, env_path: Path | None = None) -> None:
        self._env_path = env_path or default_backend_env_path()
        self._dotenv_loaded = False
        self._gemini_client: Any = None
        self._gemini_model_id = DEFAULT_GEMINI_MODEL

    @classmethod
    def instance(cls, env_path: Path | None = None) -> Keymaker:
        if cls._instance is None:
            cls._instance = cls(env_path=env_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = None

    def load_env(self) -> None:
        if self._dotenv_loaded:
            return
        from dotenv import load_dotenv

        load_dotenv(self._env_path)
        self._dotenv_loaded = True
        self._bootstrap_gemini()

    def _bootstrap_gemini(self) -> None:
        from google import genai

        key = (os.getenv("GEMINI_API_KEY") or "").strip()
        if not key:
            self._gemini_client = None
            return
        model_id = self._normalize_model_id(os.getenv("GEMINI_MODEL") or self._gemini_model_id)
        self._gemini_model_id = model_id or DEFAULT_GEMINI_MODEL
        self._gemini_client = genai.Client(api_key=key)

    @staticmethod
    def _normalize_model_id(model_id: str) -> str:
        model_id = model_id.strip()
        if model_id.startswith("models/"):
            model_id = model_id.removeprefix("models/")
        return model_id

    def _models_to_try(self) -> list[str]:
        return models_to_try(self._gemini_model_id)

    def generate_content(self, prompt: str) -> Any:
        """동기 generate_content — Smith가 429 시 모델 폴백."""
        self.load_env()
        if not self.is_gemini_ready():
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")
        return generate_with_fallback(
            client=self._gemini_client,
            prompt=prompt,
            models=self._models_to_try(),
        )

    def get_secret(self, name: str, default: str = "") -> str:
        """임의 환경 변수(민감 값) 조회. BUILDING_HUB_API_KEY, JWT_SECRET 등."""
        self.load_env()
        return (os.getenv(name) or default).strip()

    def get_gemini_api_key(self) -> str:
        self.load_env()
        return (os.getenv("GEMINI_API_KEY") or "").strip()

    def get_gemini_model_name(self) -> str:
        self.load_env()
        return self._gemini_model_id

    def get_gemini_model(self) -> Any:
        self.load_env()
        return self._gemini_client

    def is_gemini_ready(self) -> bool:
        self.load_env()
        return self._gemini_client is not None


def get_keymaker(env_path: Path | None = None) -> Keymaker:
    return Keymaker.instance(env_path=env_path)
```

### 11-1b. Prompt Engineering 상세 설계 (페르소나 & 컨텍스트 입력 규칙) ★ v8.6

Gemini는 **처방 설명 텍스트만** 생성합니다. TVI·예산·기대 개선폭은 §9·`simulate_tvi_gain()`·`BUDGET_ESTIMATE`가 **사전 확정**하고, AI는 `[데이터]` 블록의 수치를 문장으로 풀어 설명할 뿐입니다.

#### 설계 원칙 (3-Guardrail)

1. **숫자 불변(Non-Generative)** — TVI·등급·`tvi_gain_min/max`·예산·기금명은 백엔드 확정값. Gemini는 신규 숫자 추정·생성 금지 (§9와 동일).
2. **신뢰 컨텍스트(Server-Built Context)** — SSE 라우터는 `prescription_result_id`와 JWT `token`만 받음. `[데이터]` 블록은 `PrescriptionResultInteractor._build_context_prompt()`가 **서버 엔티티 조회로만** 조립 (§6-4). 클라이언트 자유 텍스트는 user 메시지에 넣지 않음.
3. **출력 형식 고정** — 페르소나(§11-1)에 4섹션·600자 상한 명시. 프론트 D-05 SSE 카드 높이 가정과 정합.

#### `[데이터]` 블록 — 입력 매핑표

| 프롬프트 변수 | 출처 | 비고 |
|---|---|---|
| `village_name` | `VillageEntity.name` | `VillagePort.find_by_id` |
| `tvi_score`, `risk_level` | `TviScoreEntity` | `TviScorePort.find_by_id` |
| `prescription_name`, `category` | `PrescriptionTypeEntity` | `PrescriptionTypePort.find_by_id` |
| `priority_rank` | `PrescriptionResultEntity.priority_rank` | 1순위만 스트리밍 (D-05) |
| `tvi_gain_min/max` | `PrescriptionResultEntity` | §9 `simulate_tvi_gain()` 역산값 |
| `fund_applicable` | `PrescriptionResultEntity.fund_applicable` | `false` → "해당 없음" |
| `fund_name`, `fund_org` | `PrescriptionFundSourceEntity` | `find_eligible_by_prescription_type` |
| `budget_min/max`, `calculation_note` | `BudgetEstimateEntity` | `BudgetEstimatePort.find_by_prescription_result_id` |

#### SSE 라우터 · Mapper

```python
# adapter/inbound/mappers/prescription_result_mapper.py
@staticmethod
def to_stream_command(*, prescription_result_id: str) -> PrescriptionResultStreamCommand:
    return PrescriptionResultStreamCommand(prescription_result_id=prescription_result_id)
```

```python
# adapter/inbound/api/v1/prescription_result_router.py (기존 경로 유지)
@router.get("/{prescription_result_id}/stream")
async def stream_ai_description(
    prescription_result_id: str,
    token: str = Query(...),
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
) -> StreamingResponse:
    command = PrescriptionResultMapper.to_stream_command(
        prescription_result_id=prescription_result_id
    )
    ...
```

#### 포트 메서드 (v8.6 추가·확정)

| 포트 | 메서드 | 용도 |
|---|---|---|
| `PrescriptionResultPort` | `find_by_id` | ✅ 기존 |
| `VillagePort` | `find_by_id` | ★ v8.6 추가 |
| `TviScorePort` | `find_by_id` | ★ v8.6 추가 |
| `PrescriptionTypePort` | `find_by_id` | ★ v8.6 추가 (`find_by_code` 유지) |
| `PrescriptionFundSourcePort` | `find_eligible_by_prescription_type` | ✅ 기존 |
| `BudgetEstimatePort` | `find_by_prescription_result_id` | ★ v8.6 신규 (§6-3) |

#### 완성 예시

**User 메시지 (`_build_context_prompt` 출력):**

```
[데이터]
마을: 단양군 영춘면
TVI 점수: 12.0 (danger)
처방: 빈집 귀농인 임대주택 전환 (vacancy), 우선순위 1순위
TVI 기대 개선폭: 8.0 ~ 12.0
예산: 27,000만원 ~ 51,000만원 (근거: 추정 34채 × 채당 800~1,500만원)
기금 출처: 지방소멸대응기금(행안부)

위 [데이터]만 근거로 설명을 작성하세요. 위에 없는 숫자는 절대 만들지 마세요.
```

**기대 출력 톤:** 모든 숫자는 `[데이터]`에서 그대로 인용. "TVI 12.0 위험 등급", "예산 2.7억~5.1억원 범위", "행안부 지방소멸대응기금 매칭 가능" 등 — 신규 수치·과장 표현 없음.

> 구현 발췌: §6-4 Interactor · DTO · Provider 6-Port 주입.

### 11-2. Gemini 모델 폴백 — `core/matrix/grid_smith_agent_scaler.py`

```python
# core/matrix/grid_smith_agent_scaler.py
"""Gemini API 429(할당량) 시 모델 순차 폴백·재시도 (Smith)."""

from __future__ import annotations

from typing import Any

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-lite"
FALLBACK_GEMINI_MODELS = (
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
)


def is_quota_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    if "429" in str(exc) or "quota" in msg or "rate limit" in msg:
        return True
    return type(exc).__name__ in ("ResourceExhausted", "TooManyRequests")


def models_to_try(primary_model_id: str) -> list[str]:
    ordered: list[str] = [primary_model_id]
    for mid in FALLBACK_GEMINI_MODELS:
        if mid not in ordered:
            ordered.append(mid)
    return ordered


def generate_with_fallback(*, client: Any, prompt: str, models: list[str]) -> Any:
    last_quota_error: BaseException | None = None
    for model_id in models:
        try:
            return client.models.generate_content(model=model_id, contents=prompt)
        except Exception as e:
            if is_quota_error(e):
                last_quota_error = e
                continue
            raise
    if last_quota_error is not None:
        raise last_quota_error
    raise RuntimeError("사용 가능한 Gemini 모델이 없습니다.")
```

> **사용 규칙:** Repository·matrix collector·Provider는 `get_keymaker().get_secret(...)`만 사용. Gemini 폴백은 Smith만. ★ v8

### 11-3. PrescriptionResult Repository (NeonDB + Gemini) ★ v7.1

> **12파일 프랙탈 유지:** 구 `outbound/ai/gemini_ai_adapter.py` 로직을 **`prescription_result_repository.py` 내부 private 메서드**로 흡수. 별도 adapter 파일·클래스 없음.

```python
# adapter/outbound/repositories/prescription_result_repository.py
from collections.abc import AsyncGenerator
from typing import Any
from google import genai
from sqlalchemy.ext.asyncio import AsyncSession
from core.matrix.grid_keymaker_secret_manager import Keymaker, TOWNPULSE_PRESCRIPTION_PERSONA
from core.matrix.grid_smith_agent_scaler import is_quota_error, models_to_try
from townpulse.app.ports.output.prescription_result_port import PrescriptionResultPort
# ... entity·orm_mapper import 생략

class PrescriptionResultRepository(PrescriptionResultPort):
    def __init__(self, session: AsyncSession, keymaker: Keymaker) -> None:
        self._session = session
        self._keymaker = keymaker

    def _gemini_client_and_models(self) -> tuple[Any, list[str]]:
        client = self._keymaker.get_gemini_model()
        if client is None:
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")
        return client, models_to_try(self._keymaker.get_gemini_model_name())

    async def _stream_gemini(
        self, system: str, messages: list[dict]
    ) -> AsyncGenerator[str, None]:
        client, model_list = self._gemini_client_and_models()
        system = system or TOWNPULSE_PRESCRIPTION_PERSONA
        last_error: BaseException | None = None
        for model in model_list:
            try:
                response = await client.aio.models.generate_content_stream(
                    model=model,
                    contents=messages[0]["content"],
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system,
                        max_output_tokens=2048,
                    ),
                )
                async for chunk in response:
                    yield chunk.text
                return
            except Exception as e:
                if is_quota_error(e):
                    last_error = e
                    continue
                raise
        if last_error:
            raise last_error
        raise RuntimeError("사용 가능한 Gemini 모델이 없습니다.")

    async def stream_ai_description(
        self, system: str, messages: list[dict]
    ) -> AsyncGenerator[str, None]:
        async for chunk in self._stream_gemini(system=system, messages=messages):
            yield chunk

    # create_bulk, find_by_id, find_by_village_id — NeonDB CRUD (기존과 동일)
```

---

## 12. 인증 (JWT) ★ v7

로그인 비즈니스는 **USER 프랙탈**(`user_interactor`, `user_router`). JWT 유틸·FastAPI Depends는 **Trinity**(`core/matrix/grid_trinity_hacker_mixin.py`) — 구 `shared/auth/` 흡수.

```python
# core/matrix/grid_trinity_hacker_mixin.py
"""JWT 발급·검증 및 FastAPI Depends — Keymaker.get_secret('JWT_SECRET') 경유."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.matrix.grid_keymaker_secret_manager import get_keymaker

_bearer = HTTPBearer(auto_error=False)


def create_access_token(user_id: str, org_id: str) -> str:
    secret = get_keymaker().get_secret("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET이 설정되지 않았습니다.")
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str) -> dict:
    secret = get_keymaker().get_secret("JWT_SECRET")
    return jwt.decode(token, secret, algorithms=["HS256"])


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증 필요")
    try:
        return verify_token(credentials.credentials)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰") from e


async def verify_sse_token(token: str = Query(...)) -> dict:
    """SSE: EventSource는 헤더 불가 → ?token=JWT 쿼리 파라미터."""
    try:
        return verify_token(token)
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 SSE 토큰") from e


CurrentUser = Annotated[dict, Depends(get_current_user)]
```

### 12-1. 공개 데모 모드 — 로그인 화면 우회 ★ v8.7

> **배경:** MVP 파일럿은 사업정의서 §10-4 *"티어 분기 없이 무상 운영"* — 방문자에게 로그인 게이트를 강제하지 않음. GET 22개 라우터의 `get_current_user`는 유지하고, **데모 토큰을 자동 발급**해 로그인 폼만 스킵한다.

| | 운영(v1.0) | MVP 데모 |
|---|---|---|
| 토큰 발급 | `POST /users/login` (ID/PW) | **+ `POST /users/demo/token`** (입력 없음) |
| GET 인증 | JWT 필요 | 데모 JWT도 통과 (`scope=demo_readonly`) |
| POST/쓰기 | JWT | 데모 토큰 → **403** (`require_write_scope`) |
| 로그인 UI | 필수 | 숨김(코드 유지, v1.0 재사용) |

```python
# core/matrix/grid_trinity_hacker_mixin.py — §12 기존 함수 아래 추가

DEMO_SCOPE = "demo_readonly"
DEMO_TOKEN_TTL_HOURS = 2

def create_demo_token() -> str:
    secret = get_keymaker().get_secret("JWT_SECRET")
    payload = {
        "sub": "demo-guest",
        "org_id": "demo",
        "scope": DEMO_SCOPE,
        "exp": datetime.utcnow() + timedelta(hours=DEMO_TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


async def require_write_scope(user: dict = Depends(get_current_user)) -> dict:
    if user.get("scope") == DEMO_SCOPE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="데모 모드는 읽기 전용입니다.",
        )
    return user
```

```python
# adapter/inbound/api/v1/user_router.py — USER 프랙탈에 라우트 1개 추가

@router.post("/demo/token")
async def issue_demo_token():
    """ID/PW 없이 즉시 발급 — 데모 방문자용. IP rate limit 권장."""
    return {
        "access_token": create_demo_token(),
        "scope": DEMO_SCOPE,
        "expires_in": DEMO_TOKEN_TTL_HOURS * 3600,
    }
```

**POST 라우터 의존성 교체:** `Depends(get_current_user)` → `Depends(require_write_scope)`  
대상: `POST /prescription-results`, `POST /budget-estimates`, `POST /reports`, `POST /report-data/*`, `POST /admin/sync/trigger`

**프론트 (`lib/api/auth.ts`):** 앱 마운트 시 `ensureDemoSession()` — 토큰 없으면 `POST /api/townpulse/users/demo/token` 호출 후 `authStore`에 저장 → `/dashboard` 직행. 상세: `TownPulse_프론트엔드_개발정의서_v2_3.md` §7-6.

**내부 QA (GATE 1):** 진짜 로그인 흐름 검증용 계정은 `town.www/.env.local`의 `QA_SEED_*`만 사용 — **문서에 평문 기재 금지**. `town.www/scripts/seed/seed_qa_account.py`로 STEP 1(Alembic) 직후 1회 생성. 상세: **§12-1c**.

### 12-1c. USER 로그인·QA 시드 ★ v9.1

> **도메인 경계:** 신규 AUTH 도메인·테이블 **없음**. 로그인 비즈니스 = `#17 USER` 12파일 프랙탈. JWT 발급·검증·`require_write_scope` = **Trinity** (`grid_trinity_hacker_mixin.py`, §12·§12-1b).

#### MVP 인증 모델

| 항목 | 규칙 |
|---|---|
| 로그인 식별자 | 요청 `org_id` = **`organization.id`** (UUID 문자열). 별도 로그인 코드 없음 |
| 비밀번호 저장 | `townpulse_user.password_hash` — **bcrypt** (`passlib[bcrypt]` 또는 `bcrypt`) |
| MVP QA 계정 | **기관 1 + 사용자 1** (`role='admin'`). 조직당 N명·이메일 로그인은 v1.0 |
| Repository 조회 | `find_by_organization_id(org_id)` → 해당 org 소속 user (MVP: 1건) |

#### `POST /users/login` — 요청·응답 (USER `user_schema.py`)

```python
# adapter/inbound/api/v1/user_schema.py (발췌)

class UserLoginRequest(BaseModel):
  org_id: str       # organization.id UUID
  password: str

class UserLoginResponse(BaseModel):
  access_token: str
  org_name: str
  user_name: str
```

| HTTP | 조건 | 응답 |
|---|---|---|
| 200 | org 존재 + password 일치 | `UserLoginResponse` |
| 401 | org/user 없음 또는 password 불일치 | `{"detail": "아이디 또는 비밀번호가 올바르지 않습니다."}` |

JWT payload (정상 로그인): `sub`=user.id, `org_id`=organization.id, `exp` — **`scope` 키 없음** (쓰기 허용).

#### `user_interactor.login` — 의사코드

```python
# app/use_cases/user_interactor.py (발췌)

async def login(self, org_id: str, password: str) -> UserLoginResponse:
    org = await self._org_port.find_by_id(org_id)
    if org is None:
        raise Unauthorized("아이디 또는 비밀번호가 올바르지 않습니다.")
    user = await self._user_port.find_by_organization_id(org_id)
    if user is None or not self._user_port.verify_password(password, user.password_hash):
        raise Unauthorized("아이디 또는 비밀번호가 올바르지 않습니다.")
    await self._user_port.update_last_login(user.id)
    token = create_access_token(user_id=str(user.id), org_id=str(org.id))
    return UserLoginResponse(
        access_token=token,
        org_name=org.name,
        user_name=user.name or user.email,
    )
```

> `verify_password`는 USER Repository private — bcrypt `checkpw` 래핑. Plain password는 DB·로그에 **저장·출력 금지**.

#### `require_write_scope` 판정 (Trinity — §12-1b 보강)

| JWT `scope` | `role` (DB, JWT 미포함) | POST 쓰기 라우터 |
|---|---|---|
| `demo_readonly` | (무관) | **403** |
| 없음 (정상 로그인) | `admin` / `viewer` | **통과** (MVP: role별 POST 분기 없음) |

MVP에서 `role`은 `/users/me` 응답·감사용. v1.0에서 `admin` 전용 라우트 분기 시 Trinity Depends 확장.

#### `town.www/scripts/seed/seed_qa_account.py`

STEP 1(Alembic 18테이블) 직후 **1회** 실행. `organization` 1행 + `townpulse_user` 1행 INSERT.

| 환경변수 | 필수 | 용도 |
|---|---|---|
| `QA_SEED_ORG_ID` | ✅ | `organization.id` — 로그인 `org_id`와 동일 UUID |
| `QA_SEED_PASSWORD` | ✅ | 평문 비밀번호 → bcrypt 해시 후 `password_hash` 저장 |
| `QA_SEED_ORG_NAME` | 선택 | 기본값 `TownPulse QA` |
| `QA_SEED_USER_EMAIL` | 선택 | 기본값 `qa@townpulse.local` |
| `QA_SEED_USER_NAME` | 선택 | 기본값 `QA Admin` |

```bash
# 실행 (백엔드 구현 후)
python -m scripts.seed.seed_qa_account
```

멱등: 동일 `QA_SEED_ORG_ID`로 org가 이미 있으면 user upsert(비밀번호 갱신) 후 종료.

**운영 주의 (MVP 제출 필수):**
- SSE `GET .../stream`은 GET이라 데모 토큰 통과 — **제출 E2E용 시연 마을 2~3곳**(영춘면 `4300025000` + α)은 `seed_qa_account` 후 QA 로그인으로 처방·리포트를 **사전 생성** (Gemini stream은 클릭 시 실시간)
- `/users/demo/token`은 공개 엔드포인트 — IP rate limit 또는 CDN 단 처리 권장

> **Stretch (선택):** 히트맵 **228곳 전체** 임의 클릭 데모 → §12-1d · `seed_all_prescriptions.py` (배치 `finalize` 이후, 6/25 이후 여유 있을 때)

### 12-1d. [OPTIONAL] 데모 228마을 처방 선생성 ★ v9.2

> **제출 필수 아님** — E2E 공식 시나리오는 영춘면 1곳(§17·개발요청가이드). 본 절은 심사위원 **임의 마을 클릭** UX를 위한 stretch.

**배경:** `demo_readonly`는 `POST /prescription-results` → 403. `SNAP_*`/`TVI_SCORE`는 배치로 228곳 채워지지만 `PRESCRIPTION_RESULT`는 lazy POST 생성 → 미생성 마을은 데모에서 처방 불가.

**해결:** `POST /prescription-results` = dispatch_rule + DB insert (**Gemini 비용 0**). TVI `finalize_monthly_snap()` 직후 QA 계정으로 228곳 1회 선실행 → 데모는 GET만. AI 설명은 `GET .../stream`에서 클릭 시 실시간(SSE).

| 항목 | 규칙 |
|---|---|
| 선행 | `seed_qa_account.py` (§12-1c) · `recalculate_all()` 1회차 완료 |
| 실행 | `town.www/scripts/seed/seed_all_prescriptions.py` — `API_BASE_URL` = Railway 프로덕션 URL 가능 |
| 멱등 | `by-village`에 row 있으면 skip |
| 매칭 0건 | `양호` 등급 등 — `by-village` 빈 배열 유지 → 프론트 §13 403 폴백 |
| Gemini 캐시 | 해커톤 규모에서는 보류 (v1.0 검토) |
| PDF | `POST /report-data`도 403 — 전 마을 PDF는 **별도** QA 사전생성 필요 |

```bash
# 실행 (백엔드 Railway 배포 + finalize 이후)
API_BASE_URL=https://api.townpulse.site/api/townpulse python -m scripts.seed.seed_all_prescriptions
```

**체크리스트 (optional):**
- [ ] 웨이브7 `finalize` 완료
- [ ] `seed_all_prescriptions.py` → 로그 `실패 0`
- [ ] 데모 토큰으로 임의 마을 1~2곳 클릭 → 403 없음
- [ ] 프론트 §13 `noPrescriptionReason` 폴백 (양호 등급)

---

## 13. NeonDB 연결 설정 ★ v7

- **Neo** (`grid_neo_theone_base.py`) — `DeclarativeBase`, Alembic metadata 단일 원천  
- **Oracle** (`grid_oracle_database_manager.py`) — AsyncEngine, `get_db`, `dispose_engine`  
- `.env.local`은 **Keymaker가 로드** — Oracle은 `os.getenv("DATABASE_URL")`만 사용 (중복 load_dotenv 없음)

> **TownPulse 적용:** 드라이버 **asyncpg**, Neon `connect_args={"ssl": "require"}`. Alembic은 `SYNC_DATABASE_URL`.

### 13-1. Neo — ORM Base

```python
# core/matrix/grid_neo_theone_base.py
"""SQLAlchemy 2.0 DeclarativeBase — Alembic·ORM metadata 단일 원천 (Neo)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """`adapter/outbound/orm/*_orm.py`가 상속하는 공통 Base."""
```

### 13-2. Oracle — Engine·Session

```python
# core/matrix/grid_oracle_database_manager.py
"""Neon(PostgreSQL) 비동기 연결 — Engine·Session (Oracle). Base는 Neo."""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncGenerator, AsyncIterator
from typing import Optional

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.matrix.grid_neo_theone_base import Base

# Keymaker.load_env() 후 DATABASE_URL 사용 — Oracle은 dotenv 직접 호출하지 않음


def _normalize_async_database_url(url: str) -> str:
    """Neon sync URL → async SQLAlchemy (asyncpg)."""
    if url.startswith("postgresql+asyncpg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def normalize_sync_database_url(url: str) -> str:
    """Alembic 등 동기 마이그레이션용 URL."""
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url


DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
ASYNC_DATABASE_URL = _normalize_async_database_url(DATABASE_URL) if DATABASE_URL else ""
SYNC_DATABASE_URL = normalize_sync_database_url(DATABASE_URL) if DATABASE_URL else ""


engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def init_engine() -> None:
    """DATABASE_URL이 있을 때만 비동기 엔진·세션 팩토리를 지연 초기화합니다."""
    global engine, async_session_factory, AsyncSessionLocal

    if not ASYNC_DATABASE_URL:
        return
    if engine is not None:
        return

    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=280,
        connect_args={"ssl": "require"},
    )
    async_session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )
    AsyncSessionLocal = async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        init_engine()
    if async_session_factory is None:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL이 설정되지 않았습니다. townpulse-api/.env.local 에 Neon 연결 문자열을 추가하세요.",
        )
    async with async_session_factory() as session:
        yield session


async def get_db_optional() -> AsyncIterator[AsyncSession | None]:
    """DB가 없을 때는 None을 넘깁니다. TownPulse MVP는 NeonDB 필수 — Provider는 `get_db` 사용."""
    if not ASYNC_DATABASE_URL:
        yield None
        return
    if async_session_factory is None:
        init_engine()
    if async_session_factory is None:
        yield None
        return
    async with async_session_factory() as session:
        yield session


async def create_all_tables() -> None:
    """등록된 ORM 모델 기준으로 테이블 생성 (로컬·수업용 보조). 운영은 Alembic 사용."""
    if engine is None:
        init_engine()
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """앱 종료 시 비동기 엔진·세션 팩토리를 정리합니다."""
    global engine, async_session_factory, AsyncSessionLocal
    if engine is not None:
        await engine.dispose()
    engine = None
    async_session_factory = None
    AsyncSessionLocal = None


if ASYNC_DATABASE_URL:
    init_engine()
```

```python
# adapter/outbound/orm/region_orm.py — ORM Base 상속 예시
from sqlalchemy.orm import Mapped, mapped_column
from core.matrix.grid_neo_theone_base import Base

class RegionOrm(Base):
    __tablename__ = "region"
    ...
```

```python
# adapter/outbound/repositories/db_init.py
from core.matrix.grid_oracle_database_manager import create_all_tables

async def create_townpulse_tables() -> None:
    """main.py lifespan — 모든 *_orm.py import 후 metadata 등록 → create_all_tables."""
    import townpulse.adapter.outbound.orm  # noqa: F401 — 모델 metadata 등록
    await create_all_tables()
```

---

## 14. 환경변수

```bash
# .env.local — Keymaker가 단일 로드 (Oracle·Trinity는 os.getenv 경유)
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/townpulse?sslmode=require  # Oracle이 asyncpg URL로 변환
GEMINI_API_KEY=AIzaSy...           # Gemini API Key
GEMINI_MODEL=gemini-2.5-flash-lite # 선택 — 미설정 시 Keymaker 기본값
JWT_SECRET=your-secret-key-min-32-chars

# 공공API 8종 — 활용신청 승인 완료 ★ v8.2 (data.go.kr 계열은 계정당 1개 인증키 재사용 가능)
BUILDING_HUB_API_KEY=...           # API#1 건축HUB_건축물대장정보 (/getBrTitleInfo)
POPULATION_HOUSEHOLD_API_KEY=...   # API#2 인구·세대현황(법정동별, 15108071)
POPULATION_AGE_API_KEY=...         # API#3 성/연령별 인구수(법정동별, 15108074)
POPULATION_MIGRATION_API_KEY=...   # API#4 지역별 인구이동 현황(15108093)
FISCAL_RELIANCE_API_KEY=...        # API#5 지방재정365 재정자립도(최종) — REGION 연1회 갱신
BUS_ROUTE_API_KEY=...              # API#6 BusRouteInfoInqireService (getRouteNoList + getRouteInfoIem)
BUS_STOP_API_KEY=...               # 15098534 BusSttnInfoInqireService (getCrdntPrxmtSttnList) — MVP, 통상 동일 키
VWORLD_API_KEY=...                 # API#7 vworld — **정류소 ingest 선행** geocode
KOSIS_API_KEY=...                  # API#8 kosis — 고령화율 등

# 내부 QA (GATE 1·처방 선생성) — §12-1c · 문서에 평문 기재 금지
QA_SEED_ORG_ID=00000000-0000-4000-8000-000000000001   # organization.id = 로그인 org_id
QA_SEED_PASSWORD=...               # seed_qa_account.py가 bcrypt 해시로 저장
QA_SEED_ORG_NAME=TownPulse QA      # 선택
QA_SEED_USER_EMAIL=qa@townpulse.local
QA_SEED_USER_NAME=QA Admin
```

---

## 15. Docker + 배포 ★ v9.2 Railway (MVP)

> **MVP 기본:** Railway Web Service + **외부 NeonDB**. 프론트는 Vercel(`townpulse.site`). EC2+Docker는 v1.0 대안.

### 15-1. Dockerfile (Railway·로컬 공통)

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Railway는 PORT 환경변수 주입 — 미설정 시 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 15-2. Railway 배포

| 항목 | 설정 |
|---|---|
| 소스 | GitHub repo → `townpulse-api/` 루트 또는 Dockerfile 경로 |
| Builder | Dockerfile |
| 환경변수 | §14 전체 — `DATABASE_URL`(Neon), `JWT_SECRET`, API 키 8종, `GEMINI_API_KEY` |
| 도메인 | `*.up.railway.app` → 커스텀 `api.townpulse.site` (CNAME) |
| 플랜 | **Hobby 이상** 권장 — 무료 슬립 시 데모 콜드스타트 |
| 헬스체크 | `GET /docs` 또는 `GET /api/townpulse/dashboard/summary` (데모 토큰) |

**배치 운영 (PaaS):**
- 긴 `collect_migration_chunk`를 **단일 HTTP 요청에 몰지 말 것** — PaaS 타임아웃(수십 초~수 분)
- MVP 일정(6/23~25): `POST .../sync/collect-core` · `.../migration/{0,1,2}` · `.../finalize`를 **청크별** 호출 (로컬 curl·CI 가능)
- APScheduler 월간 cron은 인스턴스 슬립 시 미동작 — 해커톤은 **수동 sync** 우선

**CORS (`main.py`):** Vercel origin + Railway 자체 URL

```python
allow_origins=[
    "https://townpulse.site",
    "https://www.townpulse.site",
    "http://localhost:3000",
    # "https://<service>.up.railway.app",  # 스테이징
],
```

**시드 스크립트:** `seed_qa_account`·`seed_all_prescriptions`는 **로컬에서 Railway URL**로 실행 가능 (`API_BASE_URL`).

### 15-3. docker-compose (로컬 개발)
### 15-3. docker-compose (로컬 개발)

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file: .env.local
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from townpulse.adapter.inbound.api import townpulse_router
from townpulse.adapter.outbound.repositories.db_init import create_townpulse_tables
from townpulse.dependencies.public_data_sync_orchestrator_provider import (
    build_public_data_sync_interactor,
    scheduler,
    register_batch_jobs,
)
from core.matrix.grid_oracle_database_manager import dispose_engine
from core.matrix.grid_keymaker_secret_manager import get_keymaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    get_keymaker().load_env()
    await create_townpulse_tables()
    sync_interactor = await build_public_data_sync_interactor()
    register_batch_jobs(sync_interactor)
    scheduler.start()
    yield
    scheduler.shutdown()
    await dispose_engine()

app = FastAPI(
    title="TownPulse API",
    description="충북 마을생존 AI 의사결정 플랫폼",
    version="0.8.1",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://townpulse.site",
        "https://www.townpulse.site",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(townpulse_router, prefix="/api")
```

---

## 16. Alembic 마이그레이션

```python
# alembic/env.py — Neo Base metadata, Oracle SYNC_DATABASE_URL
from core.matrix.grid_neo_theone_base import Base
from core.matrix.grid_oracle_database_manager import SYNC_DATABASE_URL

target_metadata = Base.metadata
# config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)
```

```bash
alembic revision --autogenerate -m "create_townpulse_18_tables"
alembic upgrade head
alembic downgrade -1
```

---

## 17. 프론트-백 연동 계약

| 항목 | 규칙 | 비고 |
|---|---|---|
| `emd_code` 타입 | 10자리 **문자열** VARCHAR(10) | `"4300025000"` — 앞자리 0 보존 |
| 예산 단위 | **만원 단위 정수** | `budget_min: 27000` = 2.7억원 |
| `risk_level` 값 | `"danger"` / `"warning"` / `"safe"` | 영문. `tvi_label`에 한국어 별도 제공 |
| `tvi_label` 값 | `"위험"` / `"주의"` / `"안전"` | 화면 표시용 한국어 |
| `rollout_timeline` 값 | `"urgent"` / `"medium"` / `"long"` | 영문. 프론트에서 변환 |
| `priority_rank` 타입 | 정수 `1`, `2`, `3` | 문자열 `"1순위"` 아님 |
| SSE 토큰 | `?token={JWT}` 쿼리 파라미터 | EventSource 헤더 불가 |
| 날짜·시간 | ISO 8601 UTC 문자열 | `"2026-06-01T00:00:00Z"` — 프론트에서 KST 변환 |
| CORS origin | `https://townpulse.site` | `townpulse.kr` 아님 |

---

## 18. MVP 개발 체크리스트

### Phase 1 — 공유 인프라

- [ ] Python 3.12 venv 생성 + requirements.txt 설치
- [ ] `.env.local` 작성 (NeonDB URL + Gemini API Key + JWT_SECRET) ★ v7
- [ ] `core/matrix/grid_neo_theone_base.py` — Neo DeclarativeBase ★ v7
- [ ] `core/matrix/grid_oracle_database_manager.py` — Oracle NeonDB AsyncEngine·get_db ★ v7
- [ ] `core/matrix/grid_keymaker_secret_manager.py` — Keymaker (키·persona·Gemini Client) ★ v7
- [ ] `core/matrix/grid_smith_agent_scaler.py` — Smith Gemini 모델 폴백 ★ v7
- [ ] `core/matrix/grid_trinity_hacker_mixin.py` — Trinity JWT·Depends + `create_demo_token`·`require_write_scope` ★ v8.7
- [ ] `core/matrix/grid_morpheus_base_orchestrator.py` — Morpheus ★ v7

### Phase 2 — 공간/마을 그룹 (REGION, VILLAGE)

> ★ v6: REGION ORM에 `sigungu_code`, `legal_dong_code`(NOT NULL UNIQUE, 메인 조인키), `tago_city_code`, `fiscal_self_reliance`, `fiscal_data_year` 컬럼 반영 — §5-3④, §8 DDL 참고. `emd_code`는 nullable로 다운그레이드.

- [ ] `domain/entities/region_entity.py` — 코드체계 4종 필드 포함 ★ v6
- [ ] `domain/entities/village_entity.py`
- [ ] `domain/value_objects/village_code_vo.py`
- [ ] `app/ports/input/region_use_case.py`
- [ ] `app/ports/input/village_use_case.py`
- [ ] `app/ports/output/region_port.py`
- [ ] `app/ports/output/village_port.py`
- [ ] `app/dtos/region_dto.py`
- [ ] `app/dtos/village_dto.py`
- [ ] `app/use_cases/region_interactor.py`
- [ ] `app/use_cases/village_interactor.py`
- [ ] `adapter/inbound/api/schemas/region_schema.py`
- [ ] `adapter/inbound/api/schemas/village_schema.py`
- [ ] `adapter/inbound/mappers/region_mapper.py`
- [ ] `adapter/inbound/mappers/village_mapper.py`
- [ ] `adapter/inbound/api/v1/region_router.py`
- [ ] `adapter/inbound/api/v1/village_router.py`
- [ ] `adapter/outbound/orm/region_orm.py`
- [ ] `town.www/scripts/seed/seed_tago_city_code.py` — `tago_city_codes_chungbuk.json` → `REGION.tago_city_code` (§5-3⑥) ★ v8.7
- [ ] `town.www/scripts/seed/seed_qa_account.py` — `QA_SEED_*` → `organization` + `townpulse_user` (§12-1c) ★ v9.1
- [ ] `town.www/scripts/seed/seed_all_prescriptions.py` — **[OPTIONAL]** 228마을 처방 선생성 (§12-1d) ★ v9.2
- [ ] `adapter/outbound/orm/village_orm.py`
- [ ] `adapter/outbound/orm_mappers/region_orm_mapper.py`
- [ ] `adapter/outbound/orm_mappers/village_orm_mapper.py`
- [ ] `adapter/outbound/repositories/region_repository.py`
- [ ] `adapter/outbound/repositories/village_repository.py`
- [ ] `dependencies/region_provider.py`
- [ ] `dependencies/village_provider.py`

### Phase 3 — DB 초기화 + 더미 데이터

- [ ] `adapter/inbound/api/__init__.py` — `townpulse_router` 22개 집계 (18 + 오케스트레이터 4) ★ v8.1
- [ ] `adapter/outbound/repositories/db_init.py`
- [ ] `main.py` — lifespan, CORS, router 등록
- [ ] Alembic 마이그레이션 실행 (18개 테이블 — 오케스트레이터는 별도 테이블 없음)
- [ ] 충북 228개 읍면동 REGION + VILLAGE 더미 데이터 삽입 — `legal_dong_code`(필수) · `emd_code`(API#4용) ★ v6·v9.0
- [ ] PRESCRIPTION_TYPE 5종 시드 데이터 삽입
- [ ] DISPATCH_RULE 3종 기본 룰 삽입

### Phase 4 — 공공API 스냅샷 그룹 (SNAP_* 4개)

> ★ v6: `registered_households`는 SNAP_BUILDING이 아니라 **SNAP_POPULATION** 엔티티/ORM에 둔다 (SRP 수정, §5-3②, §8 DDL).

- [ ] `domain/entities/snap_population_entity.py` — `registered_households` 포함 ★ v6
- [ ] `domain/entities/snap_building_entity.py` — `registered_households` **제거**, `residential_buildings`만 ★ v6
- [ ] `domain/entities/snap_transport_entity.py`
- [ ] `domain/entities/snap_statistics_entity.py`
- [ ] `app/ports/input/snap_population_use_case.py`
- [ ] `app/ports/input/snap_building_use_case.py`
- [ ] `app/ports/input/snap_transport_use_case.py`
- [ ] `app/ports/input/snap_statistics_use_case.py`
- [ ] (output port, dto, interactor, schema, mapper, router, orm, orm_mapper, repository, provider) × 4
- [ ] `adapter/inbound/api/v1/snap_population_router.py` (조회 전용)
- [ ] `adapter/inbound/api/v1/snap_building_router.py`
- [ ] `adapter/inbound/api/v1/snap_transport_router.py`
- [ ] `adapter/inbound/api/v1/snap_statistics_router.py`

### Phase 5 — TVI 산출 그룹 (TVI_SCORE)

- [ ] `domain/entities/tvi_score_entity.py`
- [ ] `domain/value_objects/tvi_score_vo.py`
- [ ] `domain/value_objects/tvi_grade_vo.py`
- [ ] `app/ports/input/tvi_score_use_case.py`
- [ ] `app/ports/output/tvi_score_port.py`
- [ ] `app/dtos/tvi_score_dto.py`
- [ ] `app/use_cases/tvi_score_interactor.py` (대시보드 집계 포함)
- [ ] `adapter/inbound/api/schemas/tvi_score_schema.py`
- [ ] `adapter/inbound/mappers/tvi_score_mapper.py`
- [ ] `adapter/inbound/api/v1/tvi_score_router.py`
- [ ] `adapter/outbound/orm/tvi_score_orm.py`
- [ ] `adapter/outbound/orm_mappers/tvi_score_orm_mapper.py`
- [ ] `adapter/outbound/repositories/tvi_score_repository.py`
- [ ] `dependencies/tvi_score_provider.py`

### Phase 6 — 처방 라이브러리 그룹 (5개 테이블)

- [ ] (entity, use_case, port, dto, interactor, schema, mapper, router, orm, orm_mapper, repository, provider) × 5개 테이블
  - PRESCRIPTION_TYPE
  - PRESCRIPTION_INDICATOR
  - PRESCRIPTION_FUND_SOURCE
  - DISPATCH_RULE
  - BUDGET_UNIT_PRICE

### Phase 7 — 처방 결과 그룹 (PRESCRIPTION_RESULT, BUDGET_ESTIMATE) ★ v7

- [ ] `domain/entities/prescription_result_entity.py`
- [ ] `domain/entities/budget_estimate_entity.py`
- [ ] `domain/value_objects/prescription_priority_vo.py`
- [ ] `app/ports/input/prescription_result_use_case.py` (AI 스트리밍 포함)
- [ ] `app/ports/input/budget_estimate_use_case.py`
- [ ] `app/ports/output/prescription_result_port.py` (AI 스트리밍 메서드 포함) ★ v7
- [ ] `app/ports/output/budget_estimate_port.py`
- [ ] `app/dtos/prescription_result_dto.py`
- [ ] `app/dtos/budget_estimate_dto.py`
- [ ] `app/use_cases/prescription_result_interactor.py` (DispatchRulePort + PrescriptionResultPort 주입) ★ v7
- [ ] `app/use_cases/budget_estimate_interactor.py` (BudgetUnitPricePort 주입)
- [ ] `adapter/inbound/api/schemas/prescription_result_schema.py`
- [ ] `adapter/inbound/api/schemas/budget_estimate_schema.py`
- [ ] `adapter/inbound/mappers/prescription_result_mapper.py`
- [ ] `adapter/inbound/mappers/budget_estimate_mapper.py`
- [ ] `adapter/inbound/api/v1/prescription_result_router.py` (SSE 포함)
- [ ] `adapter/inbound/api/v1/budget_estimate_router.py`
- [ ] `adapter/outbound/orm/prescription_result_orm.py`
- [ ] `adapter/outbound/orm/budget_estimate_orm.py`
- [ ] `adapter/outbound/orm_mappers/prescription_result_orm_mapper.py`
- [ ] `adapter/outbound/orm_mappers/budget_estimate_orm_mapper.py`
- [ ] `adapter/outbound/repositories/prescription_result_repository.py` (NeonDB + Gemini SSE — 구 ai/ 흡수) ★ v7.1
- [ ] `adapter/outbound/repositories/budget_estimate_repository.py`
- [ ] `dependencies/prescription_result_provider.py` (2개 주입: result_repo(keymaker) + dispatch_repo) ★ v7.1
- [ ] `dependencies/budget_estimate_provider.py` (2개 주입: estimate_repo + unit_price_repo)

### Phase 8 — SaaS 운영 그룹 (ORGANIZATION, SUBSCRIPTION, USER, REPORT)

- [ ] (entity, use_case, port, dto, interactor, schema, mapper, router, orm, orm_mapper, repository, provider) × 4개 테이블
  - ORGANIZATION
  - SUBSCRIPTION
  - USER (로그인 §12-1c + **`POST /demo/token`** §12-1b + `seed_qa_account.py`) ★ v9.1
  - REPORT

### Phase 9 — 공공데이터 배치 (Repository + PUBLIC_DATA_SYNC_ORCHESTRATOR) ★ v8.1

- [ ] `snap_population_repository.ingest_core_from_public_api()` — API#2+#3 ★ v9.0
- [ ] `snap_population_repository.ingest_migration_from_public_api()` — API#4 §10-8-1 시/도 스윕 ★ v9.0
- [ ] `public_data_sync_orchestrator_interactor` — `collect_all_core` / `collect_migration_chunk(0..2)` / `finalize_monthly_snap` ★ v9.0
- [ ] `snap_building_repository.ingest_from_public_api()` — API#1 · §10-8b 화이트리스트·unmatched 감사 로깅 ★ v8.10
- [ ] `village_repository.update_geocode_from_vworld()` — API#7 (**transport ingest보다 먼저**) ★ v8.3
- [ ] `snap_transport_repository.ingest_for_village()` — API#6 2단계 + **15098534** 정류소 ★ v8.3
- [ ] `snap_statistics_repository.ingest_from_public_api()` — API#8
- [ ] `region_repository.ingest_fiscal_self_reliance()` — API#5 연1회
- [ ] `tvi_score_repository.recalculate_all()` — §9
- [ ] `adapter/outbound/pipeline/` 폴더 **미존재** ★ v8
- [ ] API#2~#4·#6·15098534 probe — `TownPulse_API필드검증_v2_0.md` · `tago_route_counts_chungbuk.json` ★ v8.9
- [ ] `birth_rate`, `daytime_population` — **REGION + KOSIS #8**, MVP 미적재, v1.0 ingest ★ v8.4

### Phase 10 — 오케스트레이터 그룹 (4개) ★ v8.1

#### Phase 10-A: VO AOP
- [ ] `domain/value_objects/village_snapshot_vo.py` — SNAP×4 복합 VO (등급 판정 메서드 포함)
- [ ] `domain/value_objects/sido_code_vo.py` — `SIDO_CODES` · `sido_admm_cd()` ★ v9.0
- [ ] `domain/value_objects/residential_purpose_vo.py` — `RESIDENTIAL_PURPOSE_NAMES`(7종) · `is_residential()` ★ v8.10
- [ ] `domain/value_objects/sync_job_type_vo.py` — MONTHLY_SNAP | FISCAL_YEARLY ★ v8.1
- [ ] `domain/value_objects/sync_job_status_vo.py` — PENDING | RUNNING | COMPLETED | FAILED ★ v8.1

#### Phase 10-B: DASHBOARD_ORCHESTRATOR ★ v7
- [ ] `domain/entities/dashboard_orchestrator_entity.py` ★ v7 추가
- [ ] `app/ports/input/dashboard_orchestrator_use_case.py`
- [ ] `app/ports/output/dashboard_orchestrator_port.py` ★ v7 추가
- [ ] `app/dtos/dashboard_orchestrator_dto.py`
- [ ] `app/use_cases/dashboard_orchestrator_interactor.py` — Morpheus 베이스 상속, TVI+VILLAGE+SNAP_BUILDING+SNAP_TRANSPORT UseCase 4개 주입 ★ v7
- [ ] `adapter/inbound/api/schemas/dashboard_orchestrator_schema.py`
- [ ] `adapter/inbound/mappers/dashboard_orchestrator_mapper.py`
- [ ] `adapter/inbound/api/v1/dashboard_orchestrator_router.py`
- [ ] `adapter/outbound/orm/dashboard_orchestrator_orm.py`
- [ ] `adapter/outbound/orm_mappers/dashboard_orchestrator_orm_mapper.py`
- [ ] `adapter/outbound/repositories/dashboard_orchestrator_repository.py`
- [ ] `dependencies/dashboard_orchestrator_provider.py` — UseCase 4개 Depends 체이닝

#### Phase 10-C: VILLAGE_DETAIL_ORCHESTRATOR ★ v7
- [ ] `domain/entities/village_detail_orchestrator_entity.py` ★ v7 추가
- [ ] `app/ports/input/village_detail_orchestrator_use_case.py`
- [ ] `app/ports/output/village_detail_orchestrator_port.py` ★ v7 추가
- [ ] `app/dtos/village_detail_orchestrator_dto.py`
- [ ] `app/use_cases/village_detail_orchestrator_interactor.py` — UseCase 7개 주입 (VILLAGE+SNAP×4+TVI+PRESCRIPTION_RESULT), asyncio.gather 병렬 조회 ★ v7
- [ ] `adapter/inbound/api/schemas/village_detail_orchestrator_schema.py`
- [ ] `adapter/inbound/mappers/village_detail_orchestrator_mapper.py`
- [ ] `adapter/inbound/api/v1/village_detail_orchestrator_router.py`
- [ ] `adapter/outbound/orm/village_detail_orchestrator_orm.py`
- [ ] `adapter/outbound/orm_mappers/village_detail_orchestrator_orm_mapper.py`
- [ ] `adapter/outbound/repositories/village_detail_orchestrator_repository.py`
- [ ] `dependencies/village_detail_orchestrator_provider.py` — UseCase 7개 Depends 체이닝

#### Phase 10-D: REPORT_ORCHESTRATOR ★ v7
- [ ] `domain/entities/report_orchestrator_entity.py` ★ v7 추가
- [ ] `app/ports/input/report_orchestrator_use_case.py`
- [ ] `app/ports/output/report_orchestrator_port.py` ★ v7 추가
- [ ] `app/dtos/report_orchestrator_dto.py`
- [ ] `app/use_cases/report_orchestrator_interactor.py` — village_detail_orchestrator + BUDGET_ESTIMATE + ORGANIZATION UseCase 주입, village_detail 재사용 ★ v7
- [ ] `adapter/inbound/api/schemas/report_orchestrator_schema.py`
- [ ] `adapter/inbound/mappers/report_orchestrator_mapper.py`
- [ ] `adapter/inbound/api/v1/report_orchestrator_router.py`
- [ ] `adapter/outbound/orm/report_orchestrator_orm.py`
- [ ] `adapter/outbound/orm_mappers/report_orchestrator_orm_mapper.py`
- [ ] `adapter/outbound/repositories/report_orchestrator_repository.py`
- [ ] `dependencies/report_orchestrator_provider.py` — village_detail_orchestrator Depends 체이닝 재사용

#### Phase 10-E: PUBLIC_DATA_SYNC_ORCHESTRATOR ★ v8.1
- [ ] `domain/entities/public_data_sync_orchestrator_entity.py`
- [ ] `app/ports/input/public_data_sync_orchestrator_use_case.py`
- [ ] `app/ports/output/public_data_sync_orchestrator_port.py`
- [ ] `app/dtos/public_data_sync_orchestrator_dto.py`
- [ ] `app/use_cases/public_data_sync_orchestrator_interactor.py` — Morpheus 상속, Output Port 7개 + sync Port 주입, collect_all 순차 루프
- [ ] `adapter/inbound/api/schemas/public_data_sync_orchestrator_schema.py`
- [ ] `adapter/inbound/mappers/public_data_sync_orchestrator_mapper.py`
- [ ] `adapter/inbound/api/v1/public_data_sync_orchestrator_router.py` — admin sync trigger·job 조회
- [ ] `adapter/outbound/orm/public_data_sync_orchestrator_orm.py` — `public_data_sync_job` 테이블
- [ ] `adapter/outbound/orm_mappers/public_data_sync_orchestrator_orm_mapper.py`
- [ ] `adapter/outbound/repositories/public_data_sync_orchestrator_repository.py`
- [ ] `dependencies/public_data_sync_orchestrator_provider.py` — Port 7개 Depends + APScheduler·register_batch_jobs
- [ ] Region·Village·SNAP×4·TVI Output Port에 batch 메서드(`ingest_*`, `recalculate_all`, `find_all_legal_dong_codes`) 선언

### Phase 11 — 배포 ★ v9.2 Railway

- [ ] Dockerfile — `PORT` 환경변수 (§15-1)
- [ ] Railway Web Service + Neon `DATABASE_URL`
- [ ] 커스텀 도메인 `api.townpulse.site` + Vercel `NEXT_PUBLIC_API_BASE_URL`
- [ ] GitHub Actions → Railway 배포 (선택)

---

### 아키텍처 검증 — v4~v8.1 체크 ★ v8.1

**SRP 검증 (v4 유지)**
- [ ] 라우터 파일 1개가 ERD 테이블 1개만 담당하는가?
- [ ] Interactor가 자신의 테이블 Repository Port 외 다른 테이블을 직접 접근하지 않는가?
- [ ] 크로스 테이블 조회가 필요한 경우 별도 Port 주입으로 처리되는가?
- [ ] `__init__.py`에 22개 라우터 전부 등록되어 있는가?

**오케스트레이터 + VO AOP 검증 (v7 신규)** ★ v7
- [ ] 오케스트레이터 Interactor가 전용 Output Port 또는 기존 UseCase Port를 경유하는가? (Repository 직접 접근 금지)
- [ ] 오케스트레이터 Interactor가 다른 오케스트레이터를 직접 import하지 않는가? (Provider Depends 체이닝 경유)
- [ ] asyncio.gather로 병렬 UseCase 호출이 구현되어 있는가?
- [ ] report_orchestrator가 village_detail_orchestrator를 Depends 주입으로 재사용하는가?
- [ ] VO가 domain/value_objects/에만 위치하는가? (특정 도메인 entity 내부 정의 금지)
- [ ] VO가 프랙탈 파일 구조(router, schema 등)를 갖지 않는가? (AOP 원칙)

**ERD v5.1 정합 + 경계 톨게이트 검증 (v6~v8.4 현행)** ★ v8.4
- [ ] SNAP_BUILDING 엔티티/ORM/스키마에 `registered_households`가 남아있지 않은가? (SNAP_POPULATION 소속, §5-3②)
- [ ] SNAP_POPULATION(읍면동 단위) 엔티티/ORM/스키마에 `fiscal_self_reliance`가 남아있지 않은가? (REGION 소속, §5-3③)
- [ ] REGION 엔티티/ORM에 `legal_dong_code`(NOT NULL UNIQUE, 메인 조인키), `sigungu_code`, `emd_code`(nullable), `tago_city_code` 4종이 모두 있는가? (§5-3④)
- [ ] SNAP_* Repository ingest·조회가 `legal_dong_code` 기준인가?
- [ ] `snap_transport_repository` — §10-9 `_city_cache`·`_aggregate_stop_access`(city_code optional)·`ingest_for_village` ★ v9.4
- [ ] `tvi_score_repository` — `calculate_bus_interval_score()` 3단계 · `bus_route_count=None` 증평 회귀 ★ v9.4
- [ ] `region_repository.ingest_fiscal_self_reliance()`가 월간 collect_all과 별도 연간 cron인가?
- [ ] inbound mapper / orm_mapper 호출이 Router·Repository 함수 "내부"에서 일어나고, 별도 호출 체인 레이어로 그려지지 않았는가? (구조.md 경계 톨게이트 원칙, §4-5)
- [ ] UseCase~Repository Port 구간(안쪽 통로)에 Schema·ORM이 한 줄도 들어오지 않는가?
- [ ] `birth_rate`, `daytime_population`이 **REGION**에 있고 SNAP_POPULATION에는 없는가? (KOSIS #8, MVP TVI 미사용) ★ v8.4
- [ ] `pop_decline_score`가 **5지표 min-max 가중합**인가? (`net_youth_migration` 단독 금지) ★ v8.5
- [ ] `recalculate_all()`이 표본 min/max + **`prescription_cb_averages`** 갱신 + `calculate_tvi()` 단일 진입점인가? ★ v9.5
- [ ] `simulate_tvi_gain()`이 §9와 **동일 함수**로 Δ를 산출 · INCENTIVE γ·SOC 빈집 연계인가? ★ v9.5
- [ ] `TOWNPULSE_PRESCRIPTION_PERSONA`가 §11-1 개정안(숫자 불변)인가? ★ v8.6
- [ ] `_build_context_prompt()` 서버 조립 · `PrescriptionResultStreamCommand` ID만 수신인가? ★ v8.6
- [ ] `PrescriptionResultInteractor` Provider에 Port 6개 주입인가? ★ v8.6

**기존 검증 (v3 유지)**
- [ ] `domain/`이 FastAPI·SQLAlchemy·httpx를 import하지 않는가?
- [ ] `Interactor`가 ORM·HTTPException을 직접 사용하지 않는가?
- [ ] `Router`가 `*Repository`를 직접 인스턴스화하지 않는가?
- [ ] `Router`가 `*Schema`를 UseCase에 직접 전달하지 않는가?
- [ ] `Interactor` 반환값이 DTO인가?
- [ ] Result DTO가 Entity를 직접 담지 않고 평탄화되어 있는가?
- [ ] 모든 포트(22개 도메인 전체 및 오케스트레이터 포함)가 ABC로 정의되어 있는가? ★ v8.1
- [ ] 22개 도메인 모두 `inbound mapper`가 존재하는가?
- [ ] Gemini·공공API가 `{table}_repository.py` **private**에만 있는가? ★ v8
- [ ] `adapter/outbound/pipeline/`·`adapter/outbound/ai/` **미존재**인가? ★ v8
- [ ] public_data_sync_orchestrator_interactor에 API 파싱·TVI 산식 없음 (Port 조율만)? ★ v8.1
- [ ] `grid_batch_scheduler.py`·`grid_public_data_collector.py` **미존재**인가? ★ v8.1
- [ ] Gemini Client·API 키·persona·폴백이 Keymaker/Smith 경유인가? ★ v7
- [ ] ORM·Alembic metadata가 Neo(`grid_neo_theone_base`) 경유인가? ★ v7
- [ ] `get_db`·Engine이 Oracle 경유인가? ★ v7
- [ ] JWT·Depends가 Trinity 경유인가? (`shared/` 잔존 없음) ★ v7
- [ ] 데모 토큰 `POST /users/demo/token`·POST 라우터 `require_write_scope` 적용? ★ v8.7
- [ ] `vacancy_score`·`bus_interval_score`가 §9-4 **선형식**인가? (min-max **미적용**) ★ v8.8
- [ ] DRT 처방이 `avg_bus_interval_min`만 변경하는가? (정류장 거리 SNAP 변경 **금지**) ★ v8.8
- [ ] 오케스트레이터 Interactor가 Morpheus 베이스를 상속하는가? ★ v7
- [ ] `grade_filter`가 Interactor에서 처리되는가?
- [ ] Provider가 HTTP·배치 cron DI 조립 지점인가? (sync APScheduler는 public_data_sync_orchestrator_provider) ★ v8.1

---

*© 2026 Pulse Lab | TownPulse 백엔드 MVP 개발정의서 v9.0 | Confidential* ★ v9.0
