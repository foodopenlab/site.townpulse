# TownPulse 전략 분석 보고서 v6.0
> 충북 마을생존 AI 의사결정 플랫폼 | Pulse Lab | 2026년 6월  
> SSOT: `TownPulse_사업정의서_v7_2.md` · `TownPulse_ERD_MVP_v6_1.md` · `TownPulse_백엔드_MVP_개발정의서_v9_5.md`

---

## 변경 이력

| 버전 | 주요 변경 내용 |
|---|---|
| v1 | 최초 전략분석 작성 |
| v2 | 사업정의서 v0.4 반영 / 내마을AI 6항목 상세 비교표 신설 / 상호보완 관계 논리 추가 / TVI 하이브리드 방식(행안부 기반) 반영 / 빈집 산출 방식 명시 / 처방 라이브러리 10종 확장 반영 / AI 기술 구조(Gemini 역할 명확화) 신설 / 매출 3시나리오 보수화 / ESG 항목 구체화 / 평가항목 대응 업데이트 |
| v3 | MVP / v1.0 / v2.0 단계 구분 전면 반영 / ERD 설계 정규화·SOLID 적용 기준 통합 (ERD·아키텍처 설계 세션 산출물 반영) / 처방 라이브러리 코드명 명시 / 단계별 테이블 수·KPI·인터페이스 명세 통합 / 구독 티어 적용 시기 명시 / 공공API MVP 실연동 5개 vs v1.0 추가 2개 구분 명시 |
| v4 | 공공데이터 9개 API 승인·Claude 전환(후속 v5·사업정의서 v7에서 정정)·ERD 18테이블·인프라 확정 |
| v5 | **사업정의서 v7·백엔드 v8.3·ERD v5 정합** — **8종 API + 15098534** (TAGO #7 삭제) · **probe 확정**(#2~#4·#6·15098534, #1 요청만 ⚠️) · **Google Gemini API** · **SNAP_TRANSPORT 정류장 접근성** · **22도메인**(PUBLIC_DATA_SYNC) · Repository ingest·22×12 프랙탈 · SWOT·STP·Q&A·평가항목 전면 갱신 |
| v5.1 | **`birth_rate`/`daytime_population` → REGION**(KOSIS #8·시군구·MVP TVI 미사용) · 건축HUB 요청 파라미터 ✅ · v1.0 `VACANCY_VERIFICATION`→KOSIS `DT_1JU1512` · ERD v5.1·백엔드 v8.4·사업정의서 v7.1 정합 |
| v5.2 | **TVI §9 정합** — 행안부 **항목** 준용·`pop_decline_score` min-max·빈집·교통 선형식 · 처방 TVI 역산 · 문서-코드 불일치(net_youth 단독) 해소 |
| v5.3 | **§10-8b 화이트리스트** — 7종(다중주택 추가)·기숙사 제외·unmatched 감사 로깅 — 백엔드 v8.10 |
| v5.4 | **§10-8-1 net_youth_migration** — 시/도 스윕·3일 분할·MVP 제출 06-26 — 백엔드 v8.11 |
| v6.0 | **버전 체계 갱신** — v8→v9_0 · v5→v6_0 · 마이너 0~9 — 백엔드 v9.0 |

---

## 1. 사업 개요

**핵심 한 줄**: 충북 마을이 사라지는 과정을 8종 공공데이터와 버스 정류소 API로 추적하고, AI가 지자체에 근거 있는 행정 처방과 예산 시뮬레이션을 제공합니다.

TownPulse는 빈집 증가 → 인구 소멸 → 교통 공백이라는 악순환 고리를 하나의 통합 플랫폼에서 실시간으로 감지하고, 지자체 담당자가 **"어느 마을을 먼저, 어떤 처방으로, 얼마의 예산으로"** 대응할지 데이터 기반으로 결정할 수 있도록 지원하는 AI 행정 의사결정 보조 시스템입니다.

### 문제 인식 — 악순환 구조

```
빈집 증가
  → 마을 소멸 가속
    → 버스 노선 축소
      → 남은 주민 고립
        → 더 빠른 소멸 (악순환)
```

| 문제 | 현황 | 기존 대응의 한계 |
|---|---|---|
| 빈집 급증 | 충북 빈집 약 4만 채 추산 | 부서별 수작업 관리, 실시간 파악 불가 |
| 인구 소멸 | 228개 읍면동 중 절반 이상 소멸위험 | 현황 파악만 가능, 예측·처방 부재 |
| 교통 공백 | 농촌 버스 노선 지속 감축 | 수요-공급 불일치, 취약계층 이동권 침해 |

### 핵심 기능

- **마을생존지수(TVI)**: 행안부 인구감소지수 체계 + TownPulse 특화 지표(빈집·교통·**정류장 접근성**) 복합 지수, 0~100점 자동 산출
- **소멸위험 히트맵**: 충북 전체 읍면동 5단계 색상 구분, 클릭 시 상세 리포트 자동 생성
- **AI 행정 처방 + 예산 시뮬레이션**: 처방 라이브러리(MVP 5종 → v1.0 10종) 기반 자동 매핑 + **Gemini API** 처방 설명 SSE + 국토부·행안부 단가 기반 예산 추정 범위

> **TVI 산출 공식 (MVP — 백엔드 §9 SSOT)**
> ```
> TVI = pop_decline_score × 0.70 + vacancy_score × 0.20 + bus_interval_score × 0.10
>
> pop_decline_score = 5지표 min-max 가중합 (①③⑤⑥ + ②밀도)
>   — 행안부와 동일 *항목*, 정규화는 TownPulse 자체 설계 (공식 원문 비공개)
> ```
> 교통: `bus_stops_within_1km == 0` 또는 `nearest_stop_distance_m > 1000` → 0점  
> 처방 TVI 기대치: §9 `simulate_tvi_gain()` 역산 (AI·외부 근거표 아님)

---

## 2. 유사 서비스 경쟁 분석

### 직접 경쟁자 (주의 필요)

| 서비스 | 운영 주체 | 유사 기능 | 차이점 |
|---|---|---|---|
| 빈집정비 통합지원시스템 (binzibe.kr) | 한국부동산원 | AI 빈집 위험 예측 지도, 머신러닝 분석 | 빈집 단일 문제만 다룸, 교통·인구 연계 없음 |
| 내마을AI (개발 중) | 충북도 + 제천시 (국토부 주도) | LLM 기반 대화형 정보서비스, 정책 시뮬레이션 | 귀촌 안내 챗봇 수준, 처방 자동 생성 미지원 |
| KT PLIP | KT | 인구 이동·유동인구 분석 | 통신 빅데이터 기반, 지자체 맞춤 처방 없음 |
| 뉴엔AI 퀘타아이 | 뉴엔AI | 빅데이터 분석, 지역소멸 분석 검토 중 | 범용 플랫폼, 빈집·교통 통합 없음 |

---

## 3. 내마을AI 심층 비교 — 경쟁이 아닌 상호보완

> **심사위원 예상 질문**: "충북도가 이미 내마을AI를 하고 있는데 뭐가 다른가요?"

### 3-1. 내마을AI 현황

2025년 7월, 충북도·제천시가 국토교통부 '2025 스마트도시 데이터허브 시범솔루션 발굴사업'에 선정되어 총 **20억 원(국비 10억 + 지방비 10억)**을 투입, LLM 기반 대화형 정보서비스(가칭 내마을AI)를 구축 중입니다.

### 3-2. 6항목 상세 비교

| 구분 | 내마을AI | TownPulse |
|---|---|---|
| **대상 사용자** | 전 국민 (귀촌 희망자) | 지자체 공무원 (행정 담당자) |
| **목적** | 이주·귀촌 정보 안내 (정보 제공) | 행정 의사결정 보조 (처방 제시) |
| **커버 범위** | 제천시 단일 | 충북 전체 228개 읍면동 |
| **접근 방식** | 챗봇 대화형 | 히트맵 + AI 처방 대시보드 |
| **핵심 기능** | 이주자 질문 응답 | 위험 마을 조기경보 + 예산 시뮬레이션 |
| **데이터 관점** | 생활인구 중심 | 빈집·인구·교통 8종 공공데이터 + 정류소 접근성 복합 |

### 3-3. 상호보완 관계

> "내마을AI는 **귀촌 희망자가 어디로 갈지** 안내합니다.
> TownPulse는 **지자체가 어느 마을을 먼저 살려야 할지** 결정을 돕습니다.
> 두 서비스는 경쟁이 아니라 정책 실행의 앞뒤 단계를 각각 담당합니다."

TownPulse가 우선순위를 잡은 마을에 내마을AI의 귀촌 유치 정책을 집중 적용하는 구조로 오히려 시너지를 만들어냅니다.

> **발표 대응 포인트**: "기존 사업은 귀촌 안내 챗봇 수준이고, TownPulse는 8종 공공데이터와 정류소 API를 통합해 행정 처방 + 예산 시뮬레이션까지 제시하는 의사결정 보조 시스템입니다. 두 서비스는 경쟁이 아니라 정책 실행의 앞뒤 단계를 담당합니다."

---

## 4. TownPulse 핵심 차별점

| 구분 | 기존 서비스 | TownPulse |
|---|---|---|
| 데이터 통합 | 단일 문제 개별 분석 | 빈집·인구·교통(노선+정류장) 3축 인과관계 통합 |
| 분석 방식 | 현황 파악 수준 | AI 예측 + 행정 처방 + 예산 시뮬레이션까지 |
| 지수 근거 | 없음 | 행안부 인구감소지수 체계 기반 + 전문가 검증 예정 |
| 예산 근거 | 담당자 경험 의존 | 국토부·행안부 단가 라이브러리 기반 추정 범위 |
| 업무 효율 | 수작업 3개월 소요 | 실시간 자동 산출 |
| 처방 생성 | 담당자 경험 의존 | LLM(Gemini) 기반 처방 설명 자동 생성 (SSE, 처방 결과 단위) |
| 확장성 | 지자체별 커스텀 개발 | SaaS 구독으로 전국 즉시 확장 |

---

## 5. SWOT 분석

### 강점 (Strengths) — 내부 긍정

- 빈집·인구·교통(노선+정류장) 3대 문제를 하나의 인과관계로 통합 분석 (국내 유일)
- **8종 공공API + 15098534** 활용신청 승인·probe 실연동으로 즉시 데모 가능
- 행안부 인구감소지수 체계 기반 TVI로 공신력 확보
- **Google Gemini API** 기반 처방 설명 SSE + 정부 단가 기반 예산 숫자 분리 설계
- TVI 단일 지수로 직관적 비교·순위화
- SaaS 구조로 전국 즉시 확장 가능
- 해커톤 기간 내 실제 작동하는 MVP 제시 가능
- 충북 특화 데이터 선점 효과 (후발 진입자 대비 모델 누적)
- ERD 정규화 + SOLID + **22×12 프랙탈** 설계로 v1.0·v2.0 확장 비용 최소화
- **인프라 확정**(NeonDB·AWS EC2·Vercel)으로 배포 리스크 최소화, 대회 제출 시점 즉시 운영 가능한 도메인(`townpulse.site`/`api.townpulse.site`) 보유

### 약점 (Weaknesses) — 내부 부정

- 3인 부트캠프 팀, 개발 리소스 제한
- 공공API 데이터 품질·갱신 주기 불안정 — **#1 건축HUB** ✅ · **KOSIS tblId** v1.0 전 · `net_youth_migration` ✅ §10-8-1
- 빈집 직접 API 부재 → 교차 추정 방식의 오분류 가능성
- B2G 영업 사이클 길고 지자체 예산 제약 존재
- 초기 브랜드·레퍼런스 전무
- AI 처방의 신뢰도·책임 소재 검증 필요
- TVI 가중치 설정의 객관성 논란 가능 (MVP 잠정값)
- 수익화까지 긴 파일럿 기간 필요

### 기회 (Opportunities) — 외부 긍정

- 행안부 지방소멸대응기금 연 1조원+ 규모 (처방 라이브러리와 직접 연계)
- 지자체 DX 의무화 정책 전국 확산
- 일본 1,718개 시정촌 절반 이상 소멸위험, 연 1조엔 예산
- 국토부 스마트도시 데이터허브 사업 확대
- 한국 공공데이터 개방 수준 세계 최고
- 귀농귀촌 정책 수요 증가
- 동남아 스마트시티 시장 개화

### 위협 (Threats) — 외부 부정

- 한국부동산원 빈집정비 통합지원시스템 기출시
- 충북·제천 '내마을AI' 정부 주도 개발 진행 중 (국비 20억 투입)
- KT·SKT 등 통신사 빅데이터 플랫폼 지자체 시장 진입
- 지자체 예산 삭감·사업 우선순위 변동 리스크
- 공공데이터 API 정책 변경 가능성
- 개인정보·데이터 보안 규제 강화
- 유사 스타트업 후발 진입 가능성

---

## 6. STP 분석

### S — 시장 세분화 (Segmentation)

| 세그먼트 | 대상 | 수요 | 시장 규모 |
|---|---|---|---|
| 지자체 행정 | 읍면동 정책 담당자, 전국 243개 지자체 | 예산 편성·사업 수립 의사결정 | TAM ~1조원 |
| 연구·컨설팅 | 인구학·도시계획 연구자, 지방연구원·학계 | 데이터 리포트·분석 수요 | 보조 시장 |
| 민간·귀농귀촌 | 부동산·개발사, 귀농귀촌 희망자 | 지역 정보·입지 분석 수요 | 보조 시장 |

### T — 타겟팅 (Targeting)

**1차 타겟: 충북 11개 시군 정책 담당자**
- 소멸위험 상위 지자체, DX 수요 급증 중
- 파일럿 → MOU → 유료 구독 전환 경로 명확
- 예상 매출: 월 200만원 × 11개 = 연 2.6억 (낙관 시나리오)
- 해커톤 주관 기관(충북도청)과의 접점으로 진입 장벽 낮음

**2차 타겟: 전국 및 해외 확장 (2028년~)**
- 충남·강원·경북 인접 광역시도
- 행안부·국토부 중앙부처 전국 표준 플랫폼 제안
- 일본 아키타현 등 소멸 선행 지역 (2029년 시장조사 착수)

**타겟 선택 근거**
> 소멸위험 지수 상위 + 공공데이터 구축 완료 + 해커톤 주관 기관과의 접점
> → 파일럿 진입 장벽 낮고, 레퍼런스 확보 후 전국 확장에 유리

### P — 포지셔닝 (Positioning)

**포지셔닝 선언문**
> "인구소멸 위기의 지자체 담당자를 위해 — 빈집·인구·교통(노선+정류장) 악순환을 8종 공공데이터로 통합 추적하고, AI가 맞춤 행정 처방 + 근거 있는 예산 시뮬레이션까지 자동 제시하는 — 국내 유일 마을생존 의사결정 플랫폼"

**포지셔닝 맵**

```
           AI 처방 제시 (高)
                  │
  뉴엔AI ─ ─ ─ ─ │ ─ ─ ─ ─ ─ ─ [TownPulse] ← 목표
                  │                    ↑
  ──────────────────────────────────────────
   단일 문제       │              통합 문제
  ──────────────────────────────────────────
  KT PLIP         │         내마을AI (충북)
  한국부동산원     │
  기존 엑셀 관리   │
                  │
           현황 파악 (低)
```

> TownPulse는 경쟁자가 없는 오른쪽 위 사분면(통합 × AI 처방)의 블루오션을 목표로 합니다.

---

## 7. TVI (마을생존지수) 산출 방법론

### 7-1. 하이브리드 설계 — 공신력 확보 전략

TVI는 두 가지 공신력 있는 체계를 결합한 복합 지수입니다.

**기반 체계: 행안부 인구감소지수 8개 지표 — 항목 준용, 산식 TownPulse 설계**

> 행안부 정규화·가중치 원문은 비공개. MVP는 `pop_decline_score`에만 충북 읍면동 표본 **min-max** + 빈집·교통 **선형식** + 잠정 가중치 상수. 상세: 백엔드 §9.

| 행안부 지표 | MVP `pop_decline_score` | 비고 |
|---|---|---|
| ① 연평균인구증감률 | ✅ | 전월 SNAP 파생 |
| ② 인구밀도 | ✅ | `SNAP_STATISTICS.pop_density` |
| ③ 청년순이동률 | ✅ | `net_youth_migration` |
| ④ 주간인구 | ❌ | v1.0 REGION(KOSIS #8) |
| ⑤ 고령화비율 | ✅ | invert min-max |
| ⑥ 유소년비율 | ✅ | 청년층(20~39) proxy — 정의 상이 선언 |
| ⑦ 조출생률 | ❌ | v1.0 REGION |
| ⑧ 재정자립도 | ❌ 종합 TVI | v1.0 보정 검토 |

**TownPulse 특화 추가 지표 (충북 농촌 특성 반영)**

| 추가 지표 | 데이터 출처 | 추가 근거 |
|---|---|---|
| 빈집 비율 | 건축HUB(`/getBrTitleInfo`) × 행안부 법정동별 인구·세대현황 교차 추정 | 충북 농촌의 물리적 공동화 직접 지표 |
| 버스 배차 간격 | `BusRouteInfoInqireService` (#6, 2단계) | 노선 공급·배차 취약 |
| 정류장 접근성 | `BusSttnInfoInqireService` (15098534) + vworld 좌표 | 1km 내 정류장 0·최근접 >1km = 교통 공백 |

### 7-2. 빈집 비율 산출 방식 (교차 추정)

빈집 직접 API가 없는 문제를 두 정식 공공데이터의 교차 추정으로 해결합니다.

```
[Step 1] 전체 주거용 건물 수 파악
  국토교통부 건축HUB 건축물대장정보 (/getBrTitleInfo, 표제부)
  → 법정동코드(legal_dong_code) 단위 조회
  → mainPurpsCdNm 화이트리스트 매칭(단독주택·다중주택·다가구주택·공동주택·아파트·연립주택·다세대주택 — 기숙사·오피스텔 제외, §10-8b)

[Step 2] "거주 중" 건물 추정
  행정안전부 법정동별 주민등록 인구 및 세대현황
  → 같은 법정동코드 단위 세대수(registered_households) = 실거주 건물로 간주

[Step 3] 빈집 추정
  빈집 추정 수 = 전체 주거용 건물 수 - 세대수
  빈집 비율(%) = 빈집 추정 수 ÷ 전체 주거용 건물 수 × 100
```

> **투명한 한계 선언**: 전입신고 미등록 실거주자 또는 계절 거주 건물을 빈집으로 오분류할 수 있습니다. 두 정식 공공데이터를 법정동코드 기준으로 교차 결합한 간접 추정값이며, v1.0에서 **KOSIS 인구주택총조사 빈집통계(`DT_1JU1512`, 시군구)** 와 대조해 `VACANCY_VERIFICATION`에 기록합니다. 국토부 빈집실태조사·binzib는 공개 REST API가 없습니다.

### 7-3. 가중치 고도화 로드맵

| 단계 | 시기 | 내용 | 인터페이스 |
|---|---|---|---|
| MVP | 2026 | min-max 정규화 + 잠정 가중치 상수 | `WeightedSumModel` — 표본 min/max 매월 갱신 |
| v1.0 | 2027 | 충북 행정 전문가 델파이 기법으로 가중치 최적화 | `ITviModel` 도입 → `DelphiModel` 교체 |
| v2.0 | 2028 | 실제 마을 소멸 사례 데이터로 머신러닝 기반 가중치 학습 | `XGBoostModel` 추가, `confidence()` 활성화 |

---

## 8. AI 기술 구조

### 8-1. 시스템 아키텍처

| 레이어 | 구성요소 | 기술스택 |
|---|---|---|
| 데이터 수집 | 8종 API + 15098534 · Repository ingest · PUBLIC_DATA_SYNC_ORCHESTRATOR | Python, FastAPI, APScheduler |
| AI 분석 | 소멸위험 예측 모델 / 이상 탐지 | scikit-learn, XGBoost, Prophet |
| 처방 라이브러리 | 처방 유형 × 단가 × 조건 매핑 | NeonDB (PostgreSQL serverless) |
| 처방 텍스트 엔진 | 처방 설명 자동 생성 (SSE) | **Google Gemini API** (Keymaker·Smith) |
| 예산 계산기 | 마을 데이터 × 단가 대입 산출 | Python (백엔드 연산) |
| 시각화 | 지도 대시보드 (라이트/다크) | Next.js 14, Leaflet.js, Recharts, next-themes |
| 인프라 | 클라우드 배포 | Vercel(`townpulse.site`) / EC2(`api.townpulse.site`) / NeonDB |

### 8-2. 클린 아키텍처 레이어 구조 (22×12 프랙탈)

```
External APIs (8종 + 15098534, probe 대부분 확정)
        ↓
vworld geocode → VILLAGE.lat/lng (교통 ingest 선행)
        ↓
PUBLIC_DATA_SYNC_ORCHESTRATOR — cron·수동 sync 조율
        ↓
{table}_repository.ingest_* — 공공API fetch·파싱·NeonDB write (private)
        ↓
tvi_score_repository.recalculate_all() — TVI 산식
        ↓
prescription_result — DISPATCH_RULE 매핑 + budget_estimate
        ↓
prescription_result_repository.stream_ai_description() — Gemini SSE (Keymaker·Smith)
        ↓
오케스트레이터 3종 (dashboard / village-detail / report-data) → Next.js
```

> **총 22도메인** = ERD 18테이블 1:1 + 오케스트레이터 4(대시보드·마을상세·리포트·**공공데이터동기화**). `adapter/outbound/pipeline/`·별도 AI adapter 파일 없음.

### 8-3. AI 처방 엔진 구조 — Gemini 역할 명확화

```
[마을 TVI 데이터]
       ↓
[처방 매핑 로직] ← 처방 라이브러리 (DB)
  조건 탐지 → 처방 유형 선택 → 단가 계산 → PRESCRIPTION_RESULT
       ↓
[Google Gemini API]
  입력: 마을 스냅샷 + 처방 유형 + 단가 범위 + 행정 persona
  출력: 처방 설명 (2~3문장, 행정 문체) — SSE
       ↓
[최종 출력]
  처방 제목 + 설명 + 예산 범위 + TVI 기대치 + 기금 신청 여부
```

> **핵심 설계 원칙**: Gemini는 **처방 설명 텍스트만** 생성합니다. 예산·TVI 기대치는 **라이브러리 + 연산**으로 산출해 "근거 없는 AI 숫자" 비판을 구조적으로 차단합니다. 프론트는 `prescription-results/{id}/stream?token=JWT`로 **1순위 처방 설명**을 스트리밍합니다 (자유 채팅 API 없음).

---

## 9. 공공데이터 활용 현황 — 8종 API + 정류소(MVP)

> v4 대비: TAGO 버스 #7 삭제(#6 통합). **15098534** MVP 추가. `town.www/scripts/api_probe`로 #2~#4·#6·15098534 **probe 확정** (`town.www/_docs/api_samples/`).

| # | 데이터명 | dataset / 서비스 | 제공기관 | 활용 목적 | MVP 연동 |
|---|---|---|---|---|---|
| 1 | 건축HUB 건축물대장 | Swagger `/getBrTitleInfo` | 국토교통부 | 빈집 비율 추정 | ✅ probe 확정 (요청·응답) |
| 2 | 인구·세대현황 | [15108071](https://www.data.go.kr/data/15108071/openapi.do) | 행정안전부 | 총인구·세대수 | ✅ probe 확정 |
| 3 | 성/연령별 인구 | [15108074](https://www.data.go.kr/data/15108074/openapi.do) | 행정안전부 | 고령화·유소년 | ✅ probe 확정 |
| 4 | 인구이동 | [15108093](https://www.data.go.kr/data/15108093/openapi.do) | 행정안전부 | 청년순이동(파생) | ✅ probe 확정 |
| 5 | 재정자립도 | data.go.kr | 행정안전부 | 재정자립도 (시군구) | ✅ MVP 실연동 |
| 6 | 버스노선 | [15098529](https://www.data.go.kr/data/15098529/openapi.do) | 국토교통부 | 노선·배차 (2단계) | ✅ probe 확정 |
| 6b | 버스정류소 (MVP) | [15098534](https://www.data.go.kr/data/15098534/openapi.do) | 국토교통부 | 정류장 접근성 | ✅ probe 확정 |
| 7 | vworld | vworld.kr | 국토부 | 지도·좌표 | ✅ MVP 실연동 |
| 8 | KOSIS | kosis.kr | 통계청 | 지역통계 보조 | ✅ MVP 실연동 |

> 승인·키 발급 완료. **#1 건축HUB 요청·응답 확정.** KOSIS `birth_rate`·`daytime_population`은 시군구→`REGION`(v1.0 ingest, MVP TVI 미사용). 상세 매핑: `TownPulse_API필드검증_v2_0.md`.

---

## 10. 예산 시뮬레이션 구조

### 10-1. 설계 원칙

TownPulse 예산 시뮬레이션은 AI가 숫자를 임의로 생성하지 않습니다. **국토부·행안부 실제 사업 단가 라이브러리**에서 마을 데이터를 대입해 추정 범위를 산출하는 구조입니다.

```
[처방 유형 라이브러리]  ×  [마을 실제 데이터]
       ↓
  추정 예산 범위 출력 (최소값 ~ 최대값)
       ↓
  TVI 기대 상승치 (§9 역산 — 단가 min~max → SNAP 변경 → 재계산)
```

### 10-2. 처방 라이브러리 단계별 확장

#### MVP 5종 (대회 제출 기준 · 2026)

| 처방 유형 | 코드 | 단가 근거 | 단위 비용 (범위) | 기금 신청 |
|---|---|---|---|---|
| 빈집 매입 | `VAC_BUY` | 국토부 빈집정비사업 | 채당 2,000~5,000만원 | ✅ 가능 |
| 빈집 리모델링 (귀농 임대) | `VAC_REMODEL` | LH 농촌 임대주택 기준 | 채당 800~1,500만원 | ✅ 가능 |
| 수요응답형 버스(DRT) 도입 | `DRT` | 국토부 DRT 시범사업 | 노선당 연 3,000~5,000만원 | ✅ 가능 |
| 귀농귀촌 정착 인센티브 | `INCENTIVE` | 행안부 지방소멸대응기금 | 가구당 500~1,000만원 | ✅ 가능 |
| 공공시설 복합화 | `SOC_COMPLEX` | 행안부 생활SOC 사업 | 건당 5억~20억원 | ✅ 가능 |

#### v1.0 추가 5종 (2027년, 총 10종) — 충북 행정 방향성 정렬

충북도가 현재 실제로 추진 중이거나 담당자가 즉시 기금 신청 가능한 사업 유형만 선별했습니다.

| # | 처방 유형 | 코드 | 커버 TVI 지표 | 충북 연결고리 |
|---|---|---|---|---|
| 6 | 마을기업 육성 지원 | `VILLAGE_CORP` | 재정자립도, 인구밀도 | 충북도 매년 공고 운영, 인구감소지역 2배 우대 |
| 7 | 농촌 빈집 철거 + 공간 정비 | `VAC_DEMOLISH` | 빈집 비율, 인구밀도 | 농촌공간정비사업 (국비 50억), 철거 후 공동공간 전환 |
| 8 | 기업 정주여건 개선 | `ENTERPRISE` | 청년순이동률, 조출생률 | 충북도 인구감소지역 기업 기숙사 조성비 지원 집행 중 |
| 9 | 지역상권 활성화 소상공인 지원 | `COMMERCE` | 재정자립도, 주간인구 | 충북도 2026년 지역상권 활성화 기본계획 수립 착수 |
| 10 | 워케이션·체류인구 거점 조성 | `WORKATION` | 청년순이동률, 인구밀도 | 2026년 지방소멸대응기금 체류인구 창출 성과 핵심지표 격상 |

#### v2.0 방향 (2028년, 총 20종)

단가 라이브러리 누적 기반으로 **복합 처방 패키지** 개념 도입. 예: "초위험 마을 패키지" = 빈집 리모델링 + DRT + 마을기업 3종 동시 처방, 예산 합산 자동 계산.

### 10-3. 처방 자동 매핑 로직

| 감지 조건 | 자동 추천 처방 | 우선순위 |
|---|---|---|
| 빈집 비율 > 30% | 빈집 매입 + 귀농 임대주택 전환 | 1순위 |
| 버스 배차 > 120분 **또는** 1km 내 정류장 0개 | DRT 수요응답형 버스 도입 | 2순위 |
| 고령화율 > 50% | 귀농귀촌 인센티브 패키지 | 2순위 |
| TVI < 30 (위험) | 복합 처방 2가지 이상 병행 | 즉시 |
| TVI 30~60 (주의) | 단일 처방 집중 | 6개월 내 |

> MVP에서 매핑 조건은 `DISPATCH_RULE` 테이블로 관리합니다. 처방 조건 변경 시 코드 배포 없이 레코드만 수정합니다.

### 10-4. 데모 시나리오 — 단양군 영춘면 (`village_code=4300025000`, TVI 12점)

```
[마을 데이터]
  전체 가구: 100가구 | 빈집 비율: 약 34% | 버스 노선: 1개
  최근접 정류장: 약 1.2km (1km 내 0개 → 교통 공백)

[처방 1] 빈집 귀농인 임대주택 전환
  예산: 2.7억 ~ 5.1억원  |  TVI +8~12점  |  기금 ✅

[처방 2] DRT 도입
  예산: 연 3,000~5,000만원  |  TVI +4~6점  |  기금 ✅

[처방 3] 귀농귀촌 인센티브
  예산: 5,000만 ~ 1억원  |  TVI +6~10점  |  기금 ✅

→ PDF 리포트 출력 + Gemini SSE로 1순위 처방 설명 실시간 시연
```

---

## 11. ERD 설계 — 단계별 테이블 구성

### 11-1. 설계 원칙 요약

ERD 설계 세션에서 1NF→3NF 정규화, 역정규화 판단, 클린 아키텍처 SRP 검토를 거쳐 확정한 구조입니다.

**역정규화 유지 항목 (전 버전 공통)**

| 컬럼 | 위치 | 유지 근거 |
|---|---|---|
| `risk_level` | `TVI_SCORE` | 히트맵 228개 읍면동 동시 렌더링 성능 |
| `tvi_delta` | `TVI_SCORE` | 전월 대비 등급 변화 알림 트리거 |
| `ai_description` | `PRESCRIPTION_RESULT` | Gemini API 재호출 비용 절감, 저장값 재사용 |

### 11-2. MVP ERD — 18개 테이블 (2026)

| 그룹 | 테이블 | 설계 근거 |
|---|---|---|
| 공간/마을 | `REGION`, `VILLAGE` | 집계 필드 제거 (SNAP_*에서 조회), `REGION`에 법정동코드·행정동코드·시군구코드·TAGO도시코드 4종 코드체계 + 재정자립도(연1회) 보유 |
| API 스냅샷 | `SNAP_POPULATION`, `SNAP_BUILDING`, `SNAP_TRANSPORT`, `SNAP_STATISTICS` | Repository ingest — Transport(**#6 + 15098534**, vworld 선행) |
| TVI 산출 | `TVI_SCORE` | `risk_level`·`tvi_delta` 역정규화 유지 |
| 처방 라이브러리 | `PRESCRIPTION_TYPE`, `PRESCRIPTION_INDICATOR`, `PRESCRIPTION_FUND_SOURCE`, `DISPATCH_RULE`, `BUDGET_UNIT_PRICE` | 1NF + OCP |
| 처방 결과 | `PRESCRIPTION_RESULT`, `BUDGET_ESTIMATE` | DIP — Gemini는 `prescription_result_repository` 내부 |
| SaaS 운영 | `ORGANIZATION`, `SUBSCRIPTION`, `USER`, `REPORT` | 구독 티어 단일 출처 원칙 |

**정규화 과정에서 초안 대비 변경 내용**

| 변경 내용 | 근거 |
|---|---|
| `DATA_SNAPSHOT` 1개 → `SNAP_*` 4개 분리 | SRP (API 스펙 변경 격리) |
| `PRESCRIPTION_INDICATOR` 신설 | 1NF (복수 지표 원자화) |
| `PRESCRIPTION_FUND_SOURCE` 신설 | 1NF (복수 기금 출처 원자화) |
| `DISPATCH_RULE` 신설 | OCP (처방 조건 코드 하드코딩 제거) |
| `ORGANIZATION.subscription_tier` 제거 | 중복 제거 (`SUBSCRIPTION`에서 단일 관리) |
| `VILLAGE` 집계 3개 필드 제거 | 중복 제거 (`SNAP_*`과 불일치 위험 차단) |
| `BUDGET_ESTIMATE.budget_unit_price_id FK` 추가 | 단가 추적 가능성 확보 |
| `registered_households` SNAP_BUILDING → SNAP_POPULATION 이전 | SRP (인구 도메인 값이 건물 어댑터 테이블에 끼어들면 안 됨) |
| `fiscal_self_reliance` 읍면동 단위 테이블 → `REGION`(시군구 단위) 이전 | 정규화 (동일 시군구 내 모든 읍면동이 값을 중복 저장하는 것 방지) |
| `birth_rate`·`daytime_population` SNAP_POPULATION → `REGION`(시군구, KOSIS #8) | 정규화 (`fiscal_self_reliance`와 동일 패턴, 법정동 공표 없음, MVP TVI 미사용) |
| `REGION` 코드 체계 4종 확정 | `legal_dong_code`·`sigungu_code`·`emd_code`·`tago_city_code` |
| SNAP_TRANSPORT 정류장 컬럼 | `nearest_stop_distance_m`, `bus_stops_within_1km` (ERD v5) |

### 11-3. v1.0 ERD — 23개 테이블 (2027)

MVP 대비 +5개 테이블 추가.

| 신규 테이블 | 역할 |
|---|---|
| `VACANCY_VERIFICATION` | 추정 빈집율 vs KOSIS 시군구 빈집(`DT_1JU1512`) 편차 기록 |
| `TVI_MODEL_VERSION` | 모델 코드·가중치 설정·검증자·활성 여부 관리 |
| `SUBSCRIPTION_POLICY` | 티어별 기능 접근 권한 테이블화 |
| `REPORT_TEMPLATE` | 리포트 포맷·템플릿 URL 관리 |
| `UNIT_PRICE_CACHE` | 단가 캐시 만료 관리 |

기존 테이블 변경 내용:

| 테이블 | 변경 내용 |
|---|---|
| `TVI_SCORE` | `tvi_model_version_id FK` 추가 |
| `PRESCRIPTION_TYPE` | 처방 5종 레코드 추가 (VILLAGE_CORP 등) |
| `SUBSCRIPTION` | `policy_id FK` 추가 → `SUBSCRIPTION_POLICY` 연결 |
| `REPORT` | `template_id FK` 추가, `report_type` 필드 추가 |

> v3에서 계획했던 `SNAP_BIZINFO`(cleaneye.go.kr)·`SNAP_REALESTATE`(reb.or.kr) 신설은 §9의 데이터 소스 로드맵 변경에 따라 v1.0 범위에서 제외되었습니다 (+7 → +5개 테이블로 재산정).

### 11-4. v2.0 ERD — 28개 테이블 (2028)

v1.0 대비 +5개 테이블 추가.

| 신규 테이블 | 역할 |
|---|---|
| `PRESCRIPTION_PACKAGE` | 복합 처방 패키지 정의 (target_risk_level 기반) |
| `PACKAGE_ITEM` | 패키지 내 처방 구성 및 적용 순서 |
| `TVI_MODEL_TRAINING` | ML 모델 훈련 샘플 수·정확도·특성 중요도 기록 |
| `ADAPTER_AUDIT_LOG` | 어댑터별 수집 상태·HTTP 상태코드·오류 메시지·재시도 횟수 |
| `REGION_BENCHMARK` | 마을 간 TVI 차이·벤치마킹 유형 기록 |

---

## 12. SOLID 설계 원칙 적용 — 단계별 기준

### 12-1. 적용 단계 요약

| 원칙 | MVP (2026) | v1.0 (2027) | v2.0 (2028) |
|---|---|---|---|
| **S** — SNAP 테이블별 Repository ingest | ✅ | ✅ | ✅ + AuditService |
| **S** — TVI 집계/계산 분리 | ✅ `tvi_score_repository` | ✅ | ✅ |
| **O** — `IPrescriptionHandler` registry | ✅ | ✅ | ✅ + PackageHandler |
| **O** — `ITviModel` 인터페이스 | ❌ 오버엔지니어링 | ✅ WeightedSum + Delphi | ✅ + XGBoost |
| **O** — `ISubscriptionPolicy` | ❌ 파일럿 단계 | ✅ | ✅ |
| **L** — `can_handle()` 선처리 | ✅ | ✅ | ✅ |
| **L** — `confidence()` 폴백 | ❌ 단일 모델 | 준비 | ✅ 활성화 |
| **I** — Repository ingest / PUBLIC_DATA_SYNC | ✅ | ✅ | ✅ |
| **I** — `IReportDataProvider` | ❌ PDF 1종 | ✅ | ✅ |
| **D** — `prescription_result_port` (Gemini) / `IRepository` | ✅ (Gemini) | ✅ | ✅ |
| **D** — `IUnitPriceProvider` 캐시 | ❌ 5종 불필요 규모 | ✅ | ✅ |

### 12-2. MVP 핵심 인터페이스 명세 (요약)

```python
# S — Repository ingest
class SnapTransportRepository:
    async def ingest_for_village(self, village_id: str) -> None:
        # vworld 좌표 → #6 2단계 + 15098534

class TviScoreRepository:
    async def recalculate_all(self) -> None: ...

# O + L — 처방 핸들러
class IPrescriptionHandler(ABC):
    def can_handle(self, village: Village) -> bool: ...
    def execute(self, village: Village, tvi: TviScore) -> PrescriptionResult: ...

# D — Gemini (prescription_result_repository 내부, Keymaker·Smith)
class PrescriptionResultRepository:
    async def stream_ai_description(self, result_id: str) -> AsyncIterator[str]: ...
```

### 12-3. v1.0 추가 인터페이스 명세

```python
# O — TVI 모델 버전 관리
class ITviModel(ABC):
    def calculate(self, indicators: Indicators) -> TviScore: ...
    def version(self) -> str: ...

class WeightedSumModel(ITviModel):   # MVP 고정 가중치 유지
    def version(self): return "weighted_sum_v1"

class DelphiModel(ITviModel):        # v1.0 전문가 보정 가중치
    def version(self): return "delphi_v1"

# O — 구독 정책 분리
class ISubscriptionPolicy(ABC):
    def can_access(self, feature: str) -> bool: ...

class BasicPolicy(ISubscriptionPolicy): ...
class StandardPolicy(ISubscriptionPolicy): ...
class PremiumPolicy(ISubscriptionPolicy): ...

# I — 리포트 읽기 인터페이스 분리
class IReportDataProvider(ABC):
    def get_village_summary(self, village_id: str) -> VillageSummary: ...
    def get_latest_tvi(self, village_id: str) -> TviSnapshot: ...
    def get_prescriptions(self, village_id: str) -> list[PrescriptionSummary]: ...

# D — 단가 조달 추상화
class IUnitPriceProvider(ABC):
    def get_price(self, code: str, unit: str) -> UnitPriceRange: ...

class DbUnitPriceProvider(IUnitPriceProvider): ...
class CachedUnitPriceProvider(IUnitPriceProvider): ...   # UNIT_PRICE_CACHE 활용
```

### 12-4. v2.0 추가 인터페이스 명세

```python
# L — confidence() 활성화 (XGBoost 신뢰도 미달 시 폴백)
class ITviModel(ABC):
    def calculate(self, indicators: Indicators) -> TviScore: ...
    def version(self) -> str: ...
    def confidence(self, indicators: Indicators) -> float: ...

class XGBoostModel(ITviModel):
    def confidence(self, indicators):
        return self._model.predict_proba(indicators)

# O — 복합 패키지 핸들러
class PackagePrescriptionHandler(IPrescriptionHandler):
    def __init__(self, handlers: list[IPrescriptionHandler]): ...
    def can_handle(self, v): return all(h.can_handle(v) for h in self.handlers)
    def execute(self, v, tvi): ...   # 패키지 내 처방 순서대로 실행

# S — 수집 감사 서비스 분리
class AdapterAuditService:
    def log(self, adapter_name: str, result: AdapterResult) -> None: ...
    def get_failures(self, since: date) -> list[AdapterAuditLog]: ...
```

---

## 13. 비즈니스 모델

### 메인 BM — 지자체 SaaS 구독 (B2G)

| 구독 티어 | 대상 | 월 구독료 | 포함 기능 | **적용 시기** |
|---|---|---|---|---|
| Basic | 군 단위 소규모 지자체 | 100만원 | 히트맵 + 기본 리포트 | **v1.0** |
| Standard | 시 단위 지자체 | 200만원 | Basic + AI 처방 + 예산 시뮬레이션 | **v1.0** |
| Premium | 광역시도 단위 | 500만원 | Standard + API 연동 + 전담 CS | **v1.0** |

> MVP 파일럿 단계에서는 티어 분기 없이 무상 운영. v1.0에서 `SUBSCRIPTION_POLICY` 테이블 기반으로 정책 실제화.

### 보조 BM

- **정부 용역 수주**: 지방소멸 대응 시스템 구축 사업 수주 (건당 5,000만~2억원)
- **데이터 리포트 판매**: 귀농귀촌 희망자, 부동산 개발사, 연구기관 대상
- **컨설팅**: 지자체 행정 DX 컨설팅

### 시장 규모

| 구분 | 규모 | 근거 |
|---|---|---|
| TAM | 약 1조원 | 전국 243개 지자체 스마트행정 시장 |
| SAM | 약 500억원 | 지방소멸 대응 행정 AI 특화 시장 |
| SOM | 약 15억원 | 충북·충남·강원 초기 3개 시도 (보수 추정) |

---

## 14. 5개년 성장 로드맵

> 지자체 예산 편성 사이클(6~12개월)을 반영한 보수적 시나리오를 기본으로 합니다.

### 연도별 목표

| 연도 | 단계 | 핵심 목표 | 서비스 버전 |
|---|---|---|---|
| 2026 | 씨앗 | 대회 수상 → 충북 2~3개 시군 무상 파일럿 MOU → 정부 창업지원금 확보 | **MVP** |
| 2027 | 발아 | 충북 3~5개 시군 유료 구독 전환 → 행안부 지방소멸대응기금 연계 용역 수주 1건 | **v1.0** |
| 2028 | 성장 | 충북 전체 + 충남·강원 확장 → 국토부·행안부 전국 제안 | **v2.0** |
| 2029 | 확장 | 전국 10개 이상 광역시도 계약 → 일본 시장 조사 착수 (JETRO 프로그램) | **v2.0+** |
| 2030 | 도약 | 국내 안정화 후 일본 파일럿 진입 → 동남아 시장 검토 | **해외** |

### 매출 전망 — 3가지 시나리오

| 연도 | 보수 (기본값) | 중간 | 낙관 |
|---|---|---|---|
| 2026 | 0 (파일럿) | 0 (파일럿) | 0 (파일럿) |
| 2027 | 5,000만 (용역 1건) | 1.2억 (3개 시군) | 2.6억 (11개 시군) |
| 2028 | 3억 (충북+1개 시도) | 7억 | 12억 |
| 2029 | 8억 (국내 확장) | 20억 | 45억 |
| 2030 | 15억 (국내 안정화) | 40억 | 100억+ |

> **보수 시나리오 근거**: 지자체 SaaS 계약은 예산 편성 → 의회 승인 → 계약까지 최소 6~12개월. 2027년 유료 전환은 2026 하반기 파일럿 시작 기준 최소 3~5개 시군이 현실적.

### 단계별 KPI

| KPI | 2026 (MVP) | 2027 (v1.0) | 2028 (v2.0) | 2029 | 2030 |
|---|---|---|---|---|---|
| 구독 지자체 수 | 0 (파일럿) | 3~5개 | 15개 | 40개 | 60개+ |
| 월 활성 사용자 | 베타 10명 | 100명 | 500명 | 2,000명 | 5,000명 |
| 분석 마을 수 | 충북 228개 | 충북 전체 | 3개 시도 | 전국 | 전국 |
| 처방 라이브러리 | 5종 | 10종 | 20종 | 30종+ | 30종+ |
| 연동 API 수 | 8종 + 15098534 | 8종+15098534 (필드 100%) | 확장 | 확장 | 확장 |
| 백엔드 도메인 | 22개 (18+오케스트4) | 22+ | — | — | — |
| ERD 테이블 수 | 18개 | 23개 | 28개 | — | — |
| 해외 진출 | — | — | — | 일본 시장조사 | 일본 파일럿 |

---

## 15. 해외 진출 전략 — 일본 (2029년 이후)

> 원칙: 한국 시장 안정화 우선. 일본은 2029년 시장 조사 착수, 2030년 파일럿 진입.

- 일본 전체 1,718개 시정촌 중 절반 이상이 소멸위험 (한국보다 10~20년 앞서 진행)
- 일본 정부 지방소멸 대응 예산 연 1조엔(약 9조원) 규모
- 2021년 디지털청 신설 후 지자체 DX 의무화 추진 중

> "한국이 일본보다 10년 늦게 지방소멸을 겪었지만, 공공데이터 성숙도는 10년 앞서 있습니다. 한국에서 검증된 AI 모델을 일본에 이식하는 것이 전략의 핵심입니다."

| 시기 | 단계 | 내용 |
|---|---|---|
| 2029년 | 시장 조사 | JETRO 프로그램 활용, 아키타·시마네 등 소멸 심각 지역 현지 조사 |
| 2030년 | 파일럿 | 일본 1~2개 지자체 소규모 파일럿 (NTT데이터 등 SI 파트너 협의) |
| 2031년~ | 확장 | 화이트라벨 파트너십으로 확산 |

---

## 16. ESG 혁신 가치

| ESG 항목 | TownPulse의 기여 |
|---|---|
| 상생협력 (S) | 지자체·주민·귀농인·소상공인이 함께 활용하는 개방형 플랫폼 |
| 일자리 창출 (S) | 빈집 정비·귀농귀촌 유치로 농촌 일자리 간접 창출 |
| 디지털 격차 해소 (S) | 농촌 교통·행정 취약계층의 접근성 개선 |
| 탄소중립 (E) | 버스 노선 최적화(DRT)로 불필요한 공차 운행 감소 |
| 윤리경영 (G) | 공공데이터 기반 투명한 행정 의사결정 지원 (처방 텍스트 vs 예산 숫자 분리 설계) |

---

## 17. 평가항목별 대응 전략

| 평가항목 | 배점 | 핵심 대응 포인트 |
|---|---|---|
| 공공데이터 활용 | 25점 | 8종 API + 15098534 probe 실연동·법정동 JOIN·정류장 접근성·빈집 교차 추정 |
| AI 혁신성 | 20점 | TVI 복합지수 + Gemini 처방 설명(SSE) + 정부 단가 라이브러리 (숫자 분리) |
| 독창성 | 15점 | 빈집·인구·교통(노선+정류장) 악순환 통합 + 예산 시뮬레이션 원스톱 |
| 완성도 | 15점 | 라이브 데모 + PDF + **22도메인·22×12 프랙탈** Hexagonal 아키텍처 |
| 발전 가능성 | 20점 | 보수적 매출 3시나리오 + MVP→v1.0→v2.0 테이블·처방·SOLID 단계별 확장 로드맵 + 국내 안정화 후 일본 진출 |
| ESG 혁신 | 5점 | 상생·일자리·탄소중립·디지털 격차 해소 자연스럽게 충족 |

---

## 18. 심사위원 예상 Q&A

**Q. "정부가 이미 하고 있는 거 아닌가요?"**
> "기존 사업(내마을AI)은 귀촌 희망자 대상 챗봇 안내 수준입니다. TownPulse는 지자체 공무원이 대상이고, 8종 공공데이터와 정류소 API를 통합해 처방 + 예산 시뮬레이션까지 제시하는 의사결정 보조 시스템입니다. 두 서비스는 정책 실행의 앞뒤 단계를 담당하는 상호보완 관계입니다."

**Q. "예산 숫자는 어디서 나온 거예요?"**
> "국토부 빈집정비사업 단가, LH 농촌 임대주택 기준, 국토부 DRT 시범사업 운영비 등 정부 공식 사업 단가를 라이브러리로 사전 정의하고, 마을의 실제 공공데이터를 대입해 추정 범위를 산출합니다. AI가 숫자를 임의로 만들지 않습니다."

**Q. "TVI 가중치 설정의 근거는요?"**
> "행안부 인구감소지수와 **동일한 8개 지표 항목**을 쓰되, 정부가 공개하지 않은 정규화 공식은 복제할 수 없어 MVP에서는 `pop_decline_score`에만 충북 읍면동 **min-max 상대 비교**를 적용하고, 빈집·교통은 §9-4 선형식을 씁니다. v1.0에서 델파이로 숫자만 최적화하고, v2.0에서 ML 학습을 거칩니다."

**Q. "처방 TVI +8~12점은 어떻게 나오나요?"**
> "AI가 지어낸 숫자가 아닙니다. 단가 라이브러리 예산 범위를 처방별 SNAP 변경 규칙(§9-5: INCENTIVE γ·SOC 빈집 연계)에 넣고, **동일 TVI §9 공식을 다시 계산**한 Δ입니다. 계수는 SNAP 연동 **잠정값**이며 v1.0 Delphi로 정식화 예정입니다."

**Q. "빈집 데이터는 어떻게 구하나요?"**
> "빈집 직접 API는 없습니다. 국토교통부 건축HUB 건축물대장정보의 전체 주거용 건물 수와 행정안전부 법정동별 주민등록 인구 및 세대현황의 세대수를 같은 법정동코드 기준으로 교차 추정하는 방식으로 산출합니다. 한계도 투명하게 선언하고 v1.0에서 **KOSIS 시군구 빈집(`DT_1JU1512`)** 과 대조해 `VACANCY_VERIFICATION`에 기록합니다."

**Q. "공공API를 전부 쓴다는데, 실제로 작동하나요?"**
> "8종 API와 버스 정류소 API(15098534) 활용신청·키 발급을 완료했습니다. `town.www/scripts/api_probe`로 **8종 전부** 실호출 JSON 필드 매핑을 확정했고(`town.www/_docs/api_samples/`), 건축HUB 요청 파라미터(`sigunguCd`+`bjdongCd`+페이징)까지 probe 완료입니다. 승인이 막힌 API는 없습니다."

**Q. "AI는 어떤 모델을 쓰나요?"**
> "**Google Gemini API**로 처방 **설명 텍스트**만 생성합니다. 예산·TVI 기대치는 정부 단가 라이브러리와 마을 데이터 연산으로 산출해 AI가 숫자를 임의로 만들지 않습니다. Gemini 호출은 `prescription_result_repository` 내부에 캡슐화되어 있고 Keymaker·Smith가 키·429 폴백을 담당합니다."

**Q. "교통 데이터는 버스 노선만 보나요?"**
> "MVP에서는 **노선·배차(#6, 2단계)** 와 **정류장 접근성(15098534)** 을 함께 봅니다. vworld로 마을 좌표를 먼저 구한 뒤, 1km 내 정류장 수와 최근접 거리를 산출합니다. 정류장이 없거나 1km 넘으면 TVI 교통 점수가 0점(교통 공백)으로 처리됩니다."

**Q. "데이터베이스·아키텍처는?"**
> "ERD **18테이블**(`TownPulse_ERD_MVP_v6_1.md`). 백엔드는 **22도메인·22×12 프랙탈**(ERD 18 + 오케스트레이터 4). 히트맵 성능을 위해 `TVI_SCORE.risk_level`·`tvi_delta`는 역정규화 유지. v1.0 23개·v2.0 28개로 단계 확장합니다."

---

*© 2026 Pulse Lab | TownPulse 전략 분석 보고서 v6.0 | Confidential*
