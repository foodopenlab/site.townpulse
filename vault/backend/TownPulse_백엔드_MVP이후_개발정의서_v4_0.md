# TownPulse — 백엔드 MVP 이후 개발정의서

> 서비스명: TownPulse | 충북 마을생존 AI 의사결정 플랫폼  
> 버전: **v4.0** | 작성일: 2026년 6월 | 팀: Pulse Lab  
> **전제:** MVP `TownPulse_백엔드_MVP_개발정의서_v9_5.md` · `TownPulse_ERD_MVP_v6_1.md` 구현 완료  
> **변경 이력:**  
> - v3.0 — MVP v4.0 시절 초안 (18라우터·Claude·EC2 기준)  
> - **v4.0 — MVP v9.5 기준선 전면 정렬** (22×12 프랙탈·Gemini·Railway·8 API) · MVP 이월 백로그 통합  
> 이 문서는 MVP 대비 **추가·변경·이월** 항목만 기술합니다.

---

## ⚠️ MVP 이후 개발 시 주의사항

```
✅ MVP v9.5 Titanic 프랙탈 구조 유지 — 22도메인(ERD 18 + 오케스트 4), 22×12 파일
✅ 신규 ERD 테이블 = {table}_* 12파일 프랙탈 + 라우터 1개 (SRP)
✅ AI: Google Gemini API — prescription_result_repository 내부 private (별도 adapter/ai 금지)
✅ 공공API: {table}_repository.ingest_* private + PUBLIC_DATA_SYNC 오케스트레이터
✅ DB: NeonDB (PostgreSQL serverless) · 배포: Railway (api.townpulse.site) · 프론트: Vercel
✅ JWT·Depends: core/matrix/grid_trinity_hacker_mixin.py (Trinity)
✅ VO: domain/value_objects/ AOP — 프랙탈 미적용

❌ IAiTextGenerator / IPublicDataAdapter / adapter/outbound/ai/ 패턴 복원 금지 (MVP v7~v8에서 흡수 완료)
❌ pipeline/ · shared/auth/ 재도입 금지

연동 계약 (MVP와 동일):
  - emd_code / village_code: 10자리 문자열
  - village_id: UUID — snap·prescription API
  - 예산: 만원 단위 정수
  - risk_level: danger | warning | safe
  - SSE: ?token=JWT
```

---

## 목차

0. [MVP 완료 기준선 (2026)](#0-mvp-완료-기준선-2026)
1. [MVP에서 이월된 백로그](#1-mvp에서-이월된-백로그)
2. [v1.0 — 충북 유료 구독 (2027)](#2-v10--충북-유료-구독-2027)
3. [v2.0 — 전국 확장 + ML (2028)](#3-v20--전국-확장--ml-2028)
4. [단계별 구조 변화 요약](#4-단계별-구조-변화-요약)
5. [프론트-백 연동 (v1.0 이후)](#5-프론트-백-연동-v10-이후)

---

## 0. MVP 완료 기준선 (2026)

| 항목 | MVP v9.5 |
|---|---|
| 도메인 | **22개** (ERD 18 + 오케스트 4) |
| 프랙탈 | **22×12** |
| 공공 API | **8종** + 정류소 **15098534** |
| TVI | `pop_decline_score` 5지표 **min-max**(월간 raw) · 빈집·교통 선형식 · §9-3-1 한계 · §9-5 SNAP연동 처방 시뮬 |
| AI | Gemini SSE (`prescription_result_repository`) |
| 인증 | USER + Trinity JWT · 데모 `demo_readonly` |
| 배포 | Railway + Neon + Vercel |
| 처방 | 5종 라이브러리 |
| 보조 테이블 (ERD 18 외) | `public_data_sync_job` 만 |

---

## 1. MVP에서 이월된 백로그

> MVP 정의서에 **[OPTIONAL]** 또는 **비채택**으로 남긴 항목. v1.0 우선순위 참고.

### 1-1. TVI min-max 왜곡 완화 — `tvi_norm_state` EMA ★ v1.0 우선

**문제 (MVP §9-3-1):** 매월 raw `(sample_min, sample_max)` 전량 교체 → 타 마을 극단값만으로 TVI·`tvi_delta` 출렁임.  
**방향 C (채택 예정):** 지수이동평균으로 min/max **완만화** — 왜곡을 **줄이되 제거하지는 않음**.

```
smoothed_min = α × raw_min + (1−α) × smoothed_min_prev
smoothed_max = α × raw_max + (1−α) × smoothed_max_prev
ALPHA = 0.3   # 잠정 — Delphi·운영 데이터로 v1.0 튜닝
```

| 항목 | 규칙 |
|---|---|
| 테이블 | `tvi_norm_state` (ERD 18 **외**, 5행 고정) |
| 소속 | `tvi_score_repository.py` private — **신규 도메인·라우터 없음** |
| ORM | `tvi_score_orm.py`에 `TviNormStateOrm` 추가 |
| 실행 시점 | `finalize_monthly_snap()` → `recalculate_all()` 내부 |
| 부트스트랩 | 이력 없으면 `smoothed = raw` |
| `simulate_tvi_gain()` | DB에서 **최신 smoothed_norms** 로드 (메모리 캐시만 가정 금지) |

```sql
CREATE TABLE tvi_norm_state (
  indicator       VARCHAR(40) PRIMARY KEY,
  smoothed_min    FLOAT NOT NULL,
  smoothed_max    FLOAT NOT NULL,
  raw_min_last    FLOAT,
  raw_max_last    FLOAT,
  updated_at      TIMESTAMP NOT NULL
);
-- 5 indicators: annual_pop_change_rate, population_density,
--   net_youth_migration, aging_ratio, youth_ratio
```

**대안 A (Baseline Anchor):** 최초 full sample min/max **고정** — 장기 비교 설득력 ↑, 추세 반영 ↓. EMA와 병행 검토 또는 `model_version` 분기.

**UI (v1.0):** D-04에 **raw 5지표 + 전월 대비** 고정 표시 — TVI 종합점수와 분리해 공무원 Q&A 대응.

### 1-2. 데모 228마을 처방·리포트 선생성

| 항목 | MVP | v1.0 |
|---|---|---|
| 처방 POST 선생성 | §12-1d optional · `seed_all_prescriptions.py` | 운영 runbook 정식화 |
| Gemini stream 캐시 | 미구현 (`ai_description IS NOT NULL` 재생) | 트래픽 증가 시 |
| PDF 전 마을 | `POST /report-data` 403 — 영춘면 등 QA 사전생성만 | 배치 또는 v1.0 권한 모델 |

### 1-3. TVI·행정 지표 확장

| 항목 | MVP | v1.0 |
|---|---|---|
| `REGION.birth_rate`·`daytime_population` | 컬럼만 · TVI 미반영 | `pop_decline_score` 편입 검토 |
| `REGION.fiscal_self_reliance` | TVI 미반영 | 종합 TVI ⑧번 편입 |
| KOSIS `DT_1JU1512` 빈집 검증 | 추정만 | `VACANCY_VERIFICATION` 테이블 |
| `TVI_MODEL_VERSION` + Delphi | 잠정 상수 | 전문가 가중치·정규화 정책 버전 관리 |

### 1-4. 인프라·운영

| 항목 | MVP | v1.0 |
|---|---|---|
| Railway 슬립 | Hobby 플랜 | 프로덕션 SLA |
| APScheduler 월간 cron | 수동 sync 우선 | Worker 분리 또는 Railway Cron |
| EC2 자체 호스팅 | 비채택 | 대규모 트래픽 시 대안 |

### 1-5. TAGO 미지원 시군 교통 데이터 — 증평군 등 ★ v1.0 검토

**MVP v9.5:** `tago_city_code` NULL이면 15098534 GPS만 수집 · `bus_route_count=None` · `calculate_bus_interval_score()` 잠정 절충(30/50). 프론트 「교통 데이터 제한적」 배지.

**v1.0 방향 (근본 해결):** 노선·배차까지 정확 반영하려면 TAGO 외 별도 소스 통합 검토.

| 후보 | 비고 |
|---|---|
| 국가교통정보센터 전국 버스정류장 표준데이터 | 시군구 코드 매핑·갱신 주기 확인 필요 |
| 지자체 DRT·마을버스 운행 데이터 | 증평군 등 소규모 시군 직접 연계 |
| TAGO `cityCode` 확장 요청 | 행정 데이터 개방 정책 의존 |

**한계 (MVP 정직 표기):** 500m~1km 구간 정류장은 카탈로그 없이 하한 추정 · 절충값은 통계 근거 아님 — `TownPulse_백엔드_MVP_개발정의서_v9_5.md` §9-4·§10-9-3.

### 1-6. 처방 시뮬·예산 UI 고도화 (MVP v9.5 이후) ★ v1.0~v2.0

**MVP v9.5 (A안 채택):** §9-5 `INCENTIVE` 동적 γ(교통·청년비율) · `SOC_COMPLEX` 빈집 비율 연계 `pop_density`. 계수(`0.30`·`0.70`/`1.20`·`0.05`)는 **잠정** — ΔTVI는 §9 역산 추적.

**MVP 비채택 → v1.0 UI·문서:**

| 항목 | 내용 | 단계 |
|---|---|---|
| 재정자립도 매칭 | `REGION.fiscal_self_reliance` 기반 자부담·국비(기금) 분할 제안 — D-05/D-06·PDF | v1.0 |
| 단가 출처 각주 | `BUDGET_UNIT_PRICE.reference_source` 툴팁·리포트 각주 강제 바인딩 | v1.0 |
| Delphi 합의 계수 | γ·SOC 계수·`SETTLEMENT_RATE_BASE` → `TVI_MODEL_VERSION` 공표 | v1.0 (§1-3 연계) |
| 실증 ML 가중 갱신 | 집행 마을 3개년 시계열 → XGBoost 등 · `TVI_MODEL_TRAINING` | v2.0 |

---

## 2. v1.0 — 충북 유료 구독 (2027)

### 2-1. 변경 동인

- §1-1 `tvi_norm_state` EMA + raw 지표 UI
- 실연동 API 확장 (산업·부동산 등)
- 처방 10종 · 구독 티어 **실제 과금**
- `TVI_MODEL_VERSION` Delphi 가중치
- KOSIS 빈집 교차 검증

### 2-2. 신규 ERD 테이블 (v1.0 +6 → 총 24)

> 각 테이블 = 라우터 1개 = 12파일 프랙탈. `UNIT_PRICE_CACHE`는 내부 인프라(라우터 없음).

| # | 테이블 | 역할 |
|---|---|---|
| +1 | `snap_bizinfo` | 산업·고용 스냅샷 |
| +2 | `snap_realestate` | 부동산 스냅샷 |
| +3 | `vacancy_verification` | 공식 빈집 vs 추정 |
| +4 | `tvi_model_version` | TVI 가중치·정규화 정책 버전 |
| +5 | `subscription_policy` | 티어별 기능 플래그 SSOT |
| +6 | `report_template` | PDF / dashboard 템플릿 |

**ERD 18 외 보조 (v1.0 추가):**

| 테이블 | 소속 |
|---|---|
| `tvi_norm_state` | `tvi_score_repository` (§1-1) |
| `public_data_sync_job` | MVP부터 유지 |

```sql
-- tvi_model_version (발췌)
CREATE TABLE tvi_model_version (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  version_code   VARCHAR(50) UNIQUE NOT NULL,
  model_type     VARCHAR(50),  -- weighted_sum | delphi | ema_alpha
  weight_config  JSONB,        -- POP_DECLINE_WEIGHTS, ALPHA, ...
  norm_policy    VARCHAR(30),  -- raw_minmax | ema | baseline_anchor
  validated_by   VARCHAR(100),
  validated_at   DATE,
  is_active      BOOLEAN DEFAULT FALSE
);

ALTER TABLE tvi_score
  ADD COLUMN tvi_model_version_id UUID REFERENCES tvi_model_version(id);
```

### 2-3. API 추가 (발췌)

| Method | 경로 | 비고 |
|---|---|---|
| GET | `/api/townpulse/tvi-model-versions` | admin |
| POST | `/api/townpulse/tvi-model-versions/{id}/activate` | TVI 전체 재산출 트리거 |
| GET | `/api/townpulse/subscription-policies` | 티어 기능 매트릭스 |

### 2-4. `ITviModel` 포트 (v1.0)

MVP `tvi_score_repository.recalculate_all()` 단일 구현 → v1.0에서 **포트 분리** 검토:

```python
# app/ports/output/tvi_model_port.py — v1.0 신규 (12파일 프랙탈은 TVI_SCORE 유지)
class ITviModelPort(ABC):
    async def recalculate_all(self, model_version_id: UUID | None = None) -> None: ...
    def calculate_tvi(self, snap: VillageSnapBundle, norms: TviNorms) -> float: ...
```

구현체: `WeightedSumEmaModel` (MVP+§1-1) → `DelphiModel` (v1.0).

---

## 3. v2.0 — 전국 확장 + ML (2028)

### 3-1. 핵심 변화

| 항목 | 내용 |
|---|---|
| 지역 | `IRegionDataSource` — 충북 외 시도 확장 |
| TVI | XGBoost + `confidence()` — 임계 미달 시 Delphi 폴백 |
| 처방 | 20종 · `PRESCRIPTION_PACKAGE` 복합 패키지 |
| 감사 | `AdapterAuditInteractor` — 공공API 품질 이력 |

### 3-2. 신규 테이블 (+5 → 총 29)

| 테이블 | 역할 |
|---|---|
| `prescription_package` | 복합 처방 묶음 |
| `package_item` | 패키지↔처방 (PRESCRIPTION_PACKAGE 하위) |
| `region_benchmark` | 유사 마을 벤치마킹 |
| `tvi_model_training` | ML 훈련 이력 |
| `adapter_audit_log` | API 어댑터 감사 |

---

## 4. 단계별 구조 변화 요약

| 버전 | ERD 테이블 | 도메인(라우터) | 처방 | TVI 정규화 | AI |
|---|---|---|---|---|---|
| **MVP v9.5** | 18 | 22 (18+오케스트4) | 5종 | raw min-max · §9-3-1 · §9-5 SNAP연동 시뮬 | Gemini |
| v1.0 | 24 | 28+ | 10종 | EMA + Delphi 버전 | Gemini |
| v2.0 | 29 | 33+ | 20종 | XGBoost + 폴백 | Gemini |

**보조 테이블 (ERD 18 외):**

| 버전 | 테이블 |
|---|---|
| MVP | `public_data_sync_job` |
| v1.0 | + `tvi_norm_state` |
| v2.0 | (변경 없음) |

---

## 5. 프론트-백 연동 (v1.0 이후)

| 항목 | v1.0 | 프론트 |
|---|---|---|
| 구독 게이팅 | `subscription_policy` 기반 403 | 업그레이드 모달 |
| TVI 모델 | `model_version`·`norm_policy` 응답 | 설정 화면 표시 |
| raw 지표 추이 | village-detail 확장 | TVI 옆 전월 대비 5지표 |
| 리포트 | `report_type` pdf \| dashboard | 템플릿 선택 |

**불변 (MVP~v2.0):** `/api/townpulse/` prefix · `village_code`(URL) vs `village_id`(API) · SSE `?token=` · 만원 단위 예산.

---

## 부록 — v3.0 대비 폐기·대체 목록

| v3.0 (구) | v4.0 (현행) |
|---|---|
| MVP v4.0 · 18라우터 | MVP **v9.5** · **22도메인** |
| Claude API | **Gemini API** (Repository 내부) |
| AWS EC2 | **Railway** |
| `IAiTextGenerator` 포트 | `prescription_result_repository` private |
| `IPublicDataAdapter` | `{table}_repository.ingest_*` |
| 실연동 5 API | **8 API** + 15098534 |
| TVI 왜곡 대응 없음 | MVP §9-3-1 문서 + v1.0 §1-1 EMA |

---

*© 2026 Pulse Lab | TownPulse 백엔드 MVP 이후 개발정의서 v4.0*
