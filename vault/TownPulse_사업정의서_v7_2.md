# TownPulse — 충북 마을생존 AI 의사결정 플랫폼
## 사업정의서 v7.2

| 항목 | 내용 |
|---|---|
| 작성일 | 2026년 6월 |
| 버전 | v7.2 → … → v7.10 → **v7.11** (**§4-4 §9-5 SNAP 연동 처방 시뮬** — γ·빈집 연계) |
| 참고 SSOT | `TownPulse_ERD_MVP_v6_1.md` · `TownPulse_백엔드_MVP_개발정의서_v9_5.md` · `TownPulse_프론트엔드_개발정의서_v2_3.md` · `TownPulse_API필드검증_v2_0.md` · `TownPulse_백엔드_MVP이후_개발정의서_v4_0.md` |
| 팀명 | Pulse Lab |
| 서비스명 | TownPulse |
| 대회명 | 2026 충청북도 공공데이터·AI 활용 창업경진대회 |
| 공모분야 | 제품 및 서비스 개발 |

---

## 1. 사업 개요

> **핵심 한 줄**
> 충북 마을이 사라지는 과정을 8종 공공데이터와 버스 정류소 API로 추적하고, AI가 지자체에 근거 있는 행정 처방과 예산 시뮬레이션을 제공합니다.

### 1-1. 서비스 정의

TownPulse는 빈집 증가 → 인구 소멸 → 교통 공백이라는 악순환 고리를 하나의 통합 플랫폼에서 실시간으로 감지하고, 지자체 담당자가 **"어느 마을을 먼저, 어떤 처방으로, 얼마의 예산으로"** 대응할지 데이터 기반으로 결정할 수 있도록 지원하는 AI 행정 의사결정 보조 시스템입니다.

### 1-2. 문제 인식

충청북도는 전국 시도 중 인구소멸 위험도 상위권에 속하며, 농촌 지역을 중심으로 세 가지 문제가 동시에 진행되고 있습니다.

| 문제 | 현황 | 기존 대응의 한계 |
|---|---|---|
| 빈집 급증 | 충북 빈집 약 4만 채 추산 | 부서별 수작업 관리, 실시간 파악 불가 |
| 인구 소멸 | 228개 읍면동 중 절반 이상 소멸위험 | 현황 파악만 가능, 예측·처방 부재 |
| 교통 공백 | 농촌 버스 노선 지속 감축 | 수요-공급 불일치, 취약계층 이동권 침해 |

이 세 가지 문제는 별개가 아니라 **하나의 인과관계 사슬**입니다.

```
빈집 증가
  → 마을 소멸 가속
    → 버스 노선 축소
      → 남은 주민 고립
        → 더 빠른 소멸 (악순환)
```

### 1-3. 솔루션

- **8종** 공공데이터 + 버스 정류소 API(15098534)를 결합·분석하는 AI 엔진 구축 (data.go.kr 활용신청 승인 완료, probe 검증 진행)
- 행안부 인구감소지수 체계 + TownPulse 특화 지표(빈집·교통·**정류장 접근성**)를 결합한 복합 지수(TVI) 자동 산출
- **Google Gemini API 기반 행정 처방 설명 자동 생성 — SSE 스트리밍 응답** (자유 채팅이 아닌 처방 결과 단위)
- **국토부·행안부 실제 사업 단가 기반 예산 시뮬레이션** — 담당자가 즉시 참고 가능한 수준으로 제공
- 대시보드·리포트 형태로 행정 실무에 즉시 활용 가능

---

## 2. 기존 서비스와의 차별성 — 내마을AI 대응

> 심사위원 예상 질문: "충북도가 이미 내마을AI를 하고 있는데 뭐가 다른가요?"

### 2-1. 내마을AI 현황

2025년 7월, 충북도·제천시가 국토교통부 '2025 스마트도시 데이터허브 시범솔루션 발굴사업'에 선정되어 총 20억 원(국비 10억 + 지방비 10억)을 투입, **LLM 기반 대화형 정보서비스(가칭 내마을AI)**를 구축 중입니다.

### 2-2. 명확한 차별점

| 구분 | 내마을AI | TownPulse |
|---|---|---|
| 대상 사용자 | 전 국민 (귀촌 희망자) | 지자체 공무원 (행정 담당자) |
| 핵심 목적 | 이주·귀촌 정보 안내 | 소멸 위험 조기경보 + 행정 의사결정 보조 |
| 커버 범위 | 제천시 단일 지역 | 충북 전체 228개 읍면동 |
| 접근 방식 | 챗봇 대화형 | 히트맵 + 복합 지수 + AI 처방 대시보드 |
| 핵심 기능 | 귀촌 희망자 질문 응답 | 위험 마을 조기경보 + **예산 시뮬레이션** |
| 데이터 관점 | 생활인구 중심 | 빈집·인구·교통 8종 공공데이터 + 정류소 접근성 복합 |

### 2-3. 상호보완 관계

> "내마을AI는 **귀촌 희망자가 어디로 갈지** 안내합니다.
> TownPulse는 **지자체가 어느 마을을 먼저 살려야 할지** 결정을 돕습니다.
> 두 서비스는 경쟁이 아니라 정책 실행의 앞뒤 단계를 각각 담당합니다."

TownPulse가 우선순위를 잡은 마을에 내마을AI의 귀촌 유치 정책을 집중 적용하는 구조로 오히려 시너지를 냅니다.

---

## 3. 공공데이터 활용 현황 — 8종 API + 정류소(MVP)

> v6.0 대비 핵심 변화: (1) 구 **TAGO 버스 폴백(#7)** 은 **#6 버스노선과 동일 서비스**로 통합 — 실질 연동 **8종**. (2) **버스정류소 API(15098534)** 를 MVP에 추가해 마을↔정류장 거리·1km 내 정류장 수를 산출. (3) `town.www/scripts/api_probe` 실호출로 #2~#4·#6·15098534 필드 **probe 확정** (`town.www/_docs/api_samples/*.json`).

| # | 데이터명 | dataset / 서비스 | 제공기관 | 활용 목적 | MVP 연동 |
|---|---|---|---|---|---|
| 1 | 건축HUB 건축물대장정보 | Swagger `/getBrTitleInfo` | 국토교통부 | 주거용 건물 수 → 빈집 비율 추정 | ✅ probe 확정 (요청·응답) |
| 2 | 법정동별 주민등록 인구 및 세대현황 | [15108071](https://www.data.go.kr/data/15108071/openapi.do) | 행정안전부 | 총인구·세대수 | ✅ probe 확정 |
| 3 | 법정동별 성/연령별 주민등록 인구수 | [15108074](https://www.data.go.kr/data/15108074/openapi.do) | 행정안전부 | 고령화율·유소년비율 | ✅ probe 확정 |
| 4 | 지역별 인구이동 현황 | [15108093](https://www.data.go.kr/data/15108093/openapi.do) | 행정안전부 | 청년순이동률(파생 집계) | ✅ probe 확정 |
| 5 | 지방재정365 재정자립도(최종) | data.go.kr | 행정안전부 | 재정자립도 (시군구, 연 1회) | ✅ MVP 실연동 |
| 6 | 버스노선정보 | [15098529](https://www.data.go.kr/data/15098529/openapi.do) `BusRouteInfoInqireService` | 국토교통부 | 노선 수·배차간격 (2단계 조회) | ✅ probe 확정 |
| 6b | 버스정류소정보 (MVP) | [15098534](https://www.data.go.kr/data/15098534/openapi.do) `BusSttnInfoInqireService` | 국토교통부 | `nearest_stop_distance_m`·`bus_stops_within_1km` | ✅ probe 확정 (2026-06-21) |
| 7 | 공간정보 오픈플랫폼 | vworld.kr | 국토부 | 지도·읍면동 **좌표**(교통 ingest 선행) | ✅ MVP 실연동 |
| 8 | 국가통계포털(KOSIS) | kosis.kr | 통계청 | 지역통계 보조 | ✅ MVP 실연동 |

> **투명한 진행 현황 선언**: 승인·키 발급·**8종 probe 확정** 완료 (`TownPulse_API필드검증_v2_0.md`, `town.www/_docs/api_samples/`). 건축HUB #1·`net_youth_migration` 집계(§10-8-1) 확정. **KOSIS tblId**는 v1.0 전.
>
> v5.0에서 v1.0 연동 예정이었던 cleaneye.go.kr·reb.or.kr은 로드맵에서 제외. 구 **9번째 API(TAGO 폴백)** 는 #6과 중복이므로 v7에서 삭제.

---

## 4. TVI (마을생존지수) 산출 방법론

### 4-1. 지수 설계 근거 — 하이브리드 방식

TVI는 두 가지 공신력 있는 체계를 결합한 복합 지수입니다.

**기반 체계 — 행안부 인구감소지수 8개 지표 (항목 준용, 산식은 TownPulse 자체 설계)**

> 행안부는 8개 **지표 항목**과 가중 체계만 공개하며, 개별 정규화 공식·가중치 수치 원문은 비공개입니다. TownPulse는 **동일 항목**을 쓰되, MVP에서는 `pop_decline_score` 5지표만 충북 읍면동 표본 **min-max**로 0~100 부분점수를 산출합니다. 상세: `TownPulse_백엔드_MVP_개발정의서_v9_5.md` §9·§9-3-1·§9-5. 정류장 1km: **§10-9**. 화이트리스트: **§10-8b**. 청년순이동: **§10-8-1**. EMA 완만화: `TownPulse_백엔드_MVP이후_개발정의서_v4_0.md` §1-1.

| 행안부 인구감소지수 지표 | MVP `pop_decline_score` 반영 | 비고 |
|---|---|---|
| ① 연평균인구증감률 | ✅ (전월 SNAP 대비 파생) | min-max |
| ② 인구밀도 | ✅ `SNAP_STATISTICS.pop_density` | min-max |
| ③ 청년순이동률 | ✅ `net_youth_migration` | min-max |
| ④ 주간인구 | ❌ | v1.0 REGION(KOSIS #8) |
| ⑤ 고령화비율 | ✅ `population_65plus / population_total` | min-max, invert |
| ⑥ 유소년비율 | ✅ 청년층 proxy (`population_youth` 20~39세) | 행안부 정의와 상이 — 투명 선언 |
| ⑦ 조출생률 | ❌ | v1.0 REGION(KOSIS #8) |
| ⑧ 재정자립도 | ❌ 종합 TVI | `REGION` 확보, v1.0 보정 검토 |

**TownPulse 특화 추가 지표 (충북 농촌 특성 반영)**

| TownPulse 추가 지표 | 데이터 출처 | 추가 근거 |
|---|---|---|
| 빈집 비율 | 건축HUB × 행안부 인구·세대현황 교차 추정 | 충북 농촌의 물리적 공동화 직접 지표 |
| 버스 배차 간격 | 국토부 `BusRouteInfoInqireService` (#6, 2단계) | 노선 공급·배차 취약 |
| 정류장 접근성 | `BusSttnInfoInqireService` (15098534) + vworld 좌표 | 노선 데이터 있을 때 1km 내 0·최근접 >1km → **확정 교통 공백** · `tago_city_code` NULL(증평군)은 GPS만·절충 점수 ★ v9.4 |

> `birth_rate`·`daytime_population`은 **KOSIS API#8**에서 **시군구 단위**로 `REGION`에 적재 (`fiscal_self_reliance`와 동일 패턴). 법정동 단위 공표가 없어 **MVP TVI 산식(0.70/0.20/0.10)에는 미사용**이며, v1.0에서 시군구 보정계수로 검토합니다.

### 4-2. 빈집 비율 산출 방식

> **빈집 직접 API가 없는 문제에 대한 TownPulse 해결 방식**

건축HUB는 건축물대장 표제부 기반으로 "빈집" 필드를 직접 제공하지 않습니다. TownPulse는 두 정식 공공데이터의 교차 추정으로 빈집 비율을 산출합니다.

```
[Step 1] 전체 주거용 건물 수 파악
  국토교통부 건축HUB 건축물대장정보 (/getBrTitleInfo, 표제부)
  → 법정동코드(legal_dong_code) 단위 조회
  → mainPurpsCdNm 화이트리스트 매칭
    (단독주택·다중주택·다가구주택·공동주택·아파트·연립주택·다세대주택 — 기숙사·오피스텔 제외, 백엔드 §10-8b)
  → 전체 주거용 건물 수 집계

[Step 2] "거주 중" 건물 추정
  행정안전부 법정동별 주민등록 인구 및 세대현황
  → 같은 법정동코드 단위 세대수(registered_households) 조회
  → 전입신고 세대 = 실거주 건물로 간주

[Step 3] 빈집 추정
  빈집 추정 수 = 전체 주거용 건물 수 - 세대수
  빈집 비율(%) = 빈집 추정 수 ÷ 전체 주거용 건물 수 × 100
```

> **투명한 한계 선언**
> 본 추정 방식은 전입신고 미등록 실거주자 또는 계절 거주 건물을 빈집으로 오분류할 수 있습니다.
> 두 개의 정식 공공데이터만을 법정동코드 기준으로 교차 결합한 간접 추정값이며,
> v1.0에서 **KOSIS 인구주택총조사 빈집통계(`DT_1JU1512`, 시군구)** 와 추정 합산값을 대조해 `VACANCY_VERIFICATION`에 기록합니다. 국토부 빈집실태조사·binzib는 공개 REST API가 없어 자동 연동 대상이 아닙니다.

### 4-3. TVI 가중치 단계별 고도화 계획

| 단계 | 시기 | 가중치 방식 | 비고 |
|---|---|---|---|
| MVP | 2026 | **`pop_decline_score` min-max** + 빈집·교통 선형식 + 잠정 가중치 상수 | 읍면동 상대 비교. `sample_min`/`max`는 매월 `finalize` 시 갱신. **§9-3-1** 한계·`tvi_delta` 해석 문서화 |
| v1.0 | 2027 | 델파이로 **가중치 숫자** 최적화 | `DelphiModel` — 정규화 **구조** 유지 |
| v2.0 | 2028 | ML 기반 가중치 학습 | `XGBoostModel` |

**MVP 종합 TVI (잠정 상수, 공개 선언)**

```
TVI = pop_decline_score × 0.70    # §9-3: 5지표 min-max 가중합
    + vacancy_score     × 0.20    # 빈집 추정 부분점수
    + bus_interval_score × 0.10   # 배차 + 정류장 접근성

pop_decline_score 내부 (잠정):
  annual_pop_change_rate 0.30 + pop_density 0.20 + net_youth_migration 0.25
  + aging_ratio 0.15 (invert) + youth_ratio 0.10

교통 점수: §9-4 `calculate_bus_interval_score` — 노선 데이터 있을 때 1km 내 0·최근접 >1km → 0점(확정 교통 공백). `bus_route_count=null`(증평군)은 0 강제 금지·절충값 ★ v9.4

점수 0~100 (낮을수록 위험) | 위험 0~30 / 주의 31~60 / 안전 61~100
```

### 4-4. 처방 TVI 기대치 (역산)

처방의 `TVI +8~12점` 등 기대치는 AI 추정이 아니라, **단가 라이브러리 예산 범위**를 처방별 SNAP 변경 규칙(§9-5: INCENTIVE **γ**·SOC **빈집 연계**)에 대입한 뒤 **동일 TVI §9 공식을 재계산**해 얻은 Δ입니다. 계수는 SNAP 연동 **잠정 가정**이며, 재정자립도 UI·Delphi 정식화는 v1.0 이월(`MVP이후 v4_0` §1-6). 상세: 백엔드 §9-5.

---

## 5. 예산 시뮬레이션 구조

### 5-1. 설계 원칙

TownPulse 예산 시뮬레이션은 AI가 숫자를 임의로 생성하지 않습니다.
**국토부·행안부 실제 사업 단가 라이브러리**에서 마을 데이터를 대입해 추정 범위를 산출하는 구조입니다.

```
[처방 유형 라이브러리]  ×  [마을 실제 데이터]
       ↓
  추정 예산 범위 출력 (최소값 ~ 최대값)
       ↓
  TVI 기대 상승치 (지표 개선 추정)
```

### 5-2. 처방 라이브러리 단계별 확장

#### MVP 5종 (대회 제출 기준 · 2026)

| 처방 유형 | 코드 | 단가 근거 출처 | 단위 비용 (범위) | 기금 신청 |
|---|---|---|---|---|
| 빈집 매입 | VAC_BUY | 국토부 빈집정비사업 | 채당 2,000~5,000만원 | ✅ 가능 |
| 빈집 리모델링 (귀농 임대) | VAC_REMODEL | LH 농촌 임대주택 기준 | 채당 800~1,500만원 | ✅ 가능 |
| 수요응답형 버스(DRT) 도입 | DRT | 국토부 DRT 시범사업 운영비 | 노선당 연 3,000~5,000만원 | ✅ 가능 |
| 귀농귀촌 정착 인센티브 | INCENTIVE | 행안부 지방소멸대응기금 지원단가 | 가구당 500~1,000만원 | ✅ 가능 |
| 공공시설 복합화 | SOC_COMPLEX | 행안부 생활SOC 사업 기준 | 건당 5억~20억원 | ✅ 가능 |

#### v1.0 추가 5종 (2027년, 총 10종) — 충북 행정 방향성 정렬

충북도가 현재 실제로 추진 중이거나 담당자가 즉시 기금 신청 가능한 사업 유형만 선별했습니다.

| # | 처방 유형 | 코드 | 커버 TVI 지표 | 단가 근거 | 충북 연결고리 |
|---|---|---|---|---|---|
| 6 | 마을기업 육성 지원 | VILLAGE_CORP | 재정자립도, 인구밀도 | 행안부 마을기업 육성사업 (신규 최대 5,000만원) | 충북도 매년 공고 운영, 인구감소지역 2배 우대 |
| 7 | 농촌 빈집 철거 + 공간 정비 | VAC_DEMOLISH | 빈집 비율, 인구밀도 | 농촌공간정비사업 (국비 50억 규모) | 철거 후 공동텃밭·주차장 전환 등 공간재구조화 |
| 8 | 기업 정주여건 개선 | ENTERPRISE | 청년순이동률, 조출생률 | 충북도 기업 정주여건 개선사업 (최대 1억원) | 충북도 인구감소지역 기업 기숙사 조성비 지원 집행 중 |
| 9 | 지역상권 활성화 소상공인 지원 | COMMERCE | 재정자립도, 주간인구 | 행안부 지방소멸대응기금 (산업·일자리 분야) | 충북도 2026년 지역상권 활성화 기본계획 수립 착수 |
| 10 | 워케이션·체류인구 거점 조성 | WORKATION | 청년순이동률, 인구밀도 | 행안부 지방소멸대응기금 (체류인구 창출 분야) | 2026년 기금 평가체계 체류인구 창출 성과 핵심지표 격상 |

#### v2.0 방향 (2028년, 총 20종)

단가 라이브러리 누적 기반으로 **복합 처방 패키지** 개념 도입.
예: "초위험 마을 패키지" = 빈집 리모델링 + DRT + 마을기업 3종 동시 처방, 예산 합산 자동 계산.

### 5-3. 처방 자동 매핑 로직

마을 TVI 데이터에서 문제 지표를 자동 탐지해 처방을 연결합니다.

| 감지 조건 | 자동 추천 처방 | 우선순위 |
|---|---|---|
| 빈집 비율 > 30% | 빈집 매입 + 귀농 임대주택 전환 | 1순위 |
| 버스 배차 > 120분 **또는** 1km 내 정류장 0개 | DRT 수요응답형 버스 도입 | 2순위 |
| 고령화율 > 50% | 귀농귀촌 인센티브 패키지 | 2순위 |
| TVI < 30 (위험) | 복합 처방 2가지 이상 병행 | 즉시 |
| TVI 30~60 (주의) | 단일 처방 집중 | 6개월 내 |

### 5-4. 예산 산출 예시 — 단양군 영춘면 (TVI 12점)

```
[마을 데이터 조회]
  전체 가구 수: 100가구   빈집 비율: 약 34% 추정   버스 노선: 1개
  최근접 정류장: 약 1.2km (1km 내 정류장 0개 → 교통 공백)

[처방 1. 빈집 귀농인 임대주택 전환]
  대상 빈집: 추정 34채  단가: 채당 800~1,500만원
  예산 범위: 2.7억 ~ 5.1억원  /  기금: ✅ 행안부 지방소멸대응기금
  TVI 기대치: +8~12점  (§9 역산: 임대 N세대 → vacancy_score·pop_decline_score 재계산)

[처방 2. 수요응답형 버스(DRT) 도입]
  대상 노선: 1개  단가: 연 3,000~5,000만원
  예산 범위: 연 3,000만 ~ 5,000만원  /  기금: ✅ 행안부 지방소멸대응기금
  TVI 기대치: +4~6점  (§9 역산 — **교통 공백이 아닌 마을** 한정. 영춘면처럼 1km 밖·정류장 0개면 DRT 단독 Δ≈0, VAC·INCENTIVE 병행 시나리오)

[처방 3. 귀농귀촌 인센티브 패키지]
  목표 유치: 10가구  단가: 가구당 500~1,000만원
  예산 범위: 5,000만 ~ 1억원  /  기금: ✅ 행안부 지방소멸대응기금
  TVI 기대치: §9-5 역산 (지역 SNAP 연동 — 교통·청년비율·빈집에 따라 Δ 가변)
```

### 5-5. 출력 형태 — "추정 범위" 원칙

> TownPulse는 "추정 범위"를 출력합니다.
> 실제 예산 편성은 담당자가 이 범위를 참고해 정밀 견적을 의뢰하는 구조입니다.

| 출력 항목 | 표현 방식 | 이유 |
|---|---|---|
| 예산 | "약 X억 ~ Y억원" (범위) | 지자체별 집행 단가 차이 반영 |
| TVI 기대치 | "+X~Y점 예상" (범위) | §9 `simulate_tvi_gain()` 역산 (단가 min~max 대입) |
| 기금 신청 | "신청 가능 / 검토 필요" | 최종 자격은 지자체 확인 필요 |
| 시행 시기 | "즉시 / 6개월 내 / 중장기" | 처방 복잡도 기반 자동 분류 |

---

## 6. AI 기술 구조

### 6-1. 시스템 아키텍처

| 레이어 | 구성요소 | 기술스택 |
|---|---|---|
| 데이터 수집 | 8종 공공API + 15098534 · `{table}_repository.ingest_*` · `PUBLIC_DATA_SYNC_ORCHESTRATOR`(cron·수동) | Python, FastAPI, APScheduler |
| AI 분석 | 소멸위험 예측 모델 / 이상 탐지 | scikit-learn, XGBoost, Prophet |
| 처방 라이브러리 | 처방 유형 × 단가 × 조건 매핑 | NeonDB (PostgreSQL serverless, 사전 정의 테이블) |
| 처방 텍스트 엔진 | 처방 설명 자동 생성 (SSE) | **Google Gemini API** (`prescription_result_repository` + Keymaker·Smith) |
| 예산 계산기 | 마을 데이터 × 단가 대입 산출 | Python (백엔드 연산) |
| 시각화 | 지도 기반 대시보드 (라이트 기본·다크 토글) | Next.js 14 (App Router), Leaflet.js, Recharts, next-themes |
| 인프라 | 클라우드 배포 | 프론트 Vercel(`townpulse.site`) / 백엔드 AWS EC2(`api.townpulse.site`) / DB NeonDB |

> v6.0 대비 v7.0: AI는 **Google Gemini API** 확정(별도 `adapter/outbound/ai/` 없음, Repository 내부 캡슐화). 수집은 pipeline 폴더 대신 **Repository ingest + PUBLIC_DATA_SYNC 오케스트레이터**. 백엔드 **22×12 프랙탈**(ERD 18 + 오케스트 4). 프론트 **Next.js 14** + 라이트/다크 테마.

### 6-2. AI 처방 엔진 구조 — Gemini 역할 명확화

```
[마을 TVI 데이터]
       ↓
[처방 매핑 로직] ← 처방 라이브러리 (DB)
  조건 탐지 → 처방 유형 선택 → 단가 계산 → PRESCRIPTION_RESULT 생성
       ↓
[Google Gemini API]  (prescription_result_repository.stream_ai_description)
  입력: 마을 스냅샷 + 선택된 처방 유형 + 단가 범위 + 행정 persona
  출력: 처방 설명 텍스트 (2~3문장, 행정 문체) — SSE 스트리밍
       ↓
[최종 출력]
  처방 제목 + 설명 + 예산 범위 + TVI 기대치 + 기금 신청 여부
```

> Gemini는 **"처방 설명 텍스트 생성"만** 담당합니다. 예산 숫자와 TVI 기대치는 **사전 정의된 라이브러리 + 마을 데이터 연산**으로 산출합니다.
> 프론트엔드는 `GET /prescription-results/{id}/stream?token=JWT` 로 **1순위 처방 설명**을 실시간 스트리밍합니다 (자유형 채팅 API 없음).

### 6-3. 핵심 기능 3가지

**① 마을 소멸위험 히트맵**
- 충북 전체 읍면동을 TVI 기반 5단계 위험도로 색상 구분
- 클릭 시 해당 마을 상세 리포트 자동 생성
- 전월 대비 등급 변화 알림

**② 악순환 지수 대시보드**
- 빈집 비율 / 인구감소율 / 버스 배차간격 / **정류장 접근성** / 고령화율 통합 시각화
- 행안부 8개 지표 기반 분석 결과 시각화
- 타 시군 벤치마킹 비교 (v2.0)

**③ AI 행정 처방 + 예산 시뮬레이션**
- Gemini 기반 처방 설명 SSE 스트리밍 생성
- 국토부·행안부 단가 라이브러리 기반 예산 추정 범위 산출
- 행안부 지방소멸대응기금 신청 가능 여부 자동 안내
- PDF 리포트로 즉시 출력 (클라이언트 html2canvas + jsPDF)

### 6-4. 백엔드 아키텍처 신뢰도

대회 제출 시점 기준, 백엔드는 Hexagonal + Clean Architecture + DDD **22×12 프랙탈** 구조로 **ERD 18테이블 1:1 라우터 18개 + 오케스트레이터 4개(대시보드·마을상세·리포트·공공데이터동기화) = 총 22개 도메인**으로 설계되어 있습니다. 외부 의존성(Gemini API, NeonDB, 공공API)은 Repository·`core/matrix`(Keymaker·Smith) 경유로 캡슐화되며, `*_interactor.py` 22개로 UseCase 회귀 검증을 자동화합니다.

---

## 7. MVP 정의 (대회 제출 범위 · 2026)

> **시제품 완성 기준**
> 대회 규정에 따라 신청 마감일 전 아래 기능이 실제 작동하는 상태로 완성됩니다.
> 심사 당일 라이브 데모 시연 가능합니다.

### 7-1. MVP 구현 범위

| 기능 | 상세 내용 | 상태 |
|---|---|---|
| 데이터 수집·적재 | 8종 API + 15098534 · Repository ingest · PUBLIC_DATA_SYNC | 제출일 완성 |
| TVI 산출 엔진 | 복합 지수 계산 (`tvi_score_repository.recalculate_all`) | 제출일 완성 |
| 소멸위험 히트맵 | 충북 전체 읍면동 실제 데이터 시각화 | 제출일 완성 |
| 상세 리포트 | 마을 클릭 시 자동 리포트 생성 | 제출일 완성 |
| 처방 라이브러리 | MVP 5종 처방 × 단가 × 조건 매핑 DB 구축 | 제출일 완성 |
| AI 처방 추천 | Gemini API 연동 처방 설명 SSE 스트리밍 | 제출일 완성 |
| 예산 시뮬레이션 | 마을 데이터 × 단가 대입 범위 산출 | 제출일 완성 |
| 대시보드 UI | 지자체 담당자용 웹 (Next.js 14, 라이트/다크) | 제출일 완성 |
| 모바일 반응형 | 현장 담당자 모바일 접근 | 제출일 완성 |
| PDF 리포트 출력 | 담당자 보고서 즉시 출력 | 제출일 완성 |

> v1.0 전 잔여: **KOSIS tblId** probe. (8종 API + 15098534 + `net_youth_migration` §10-8-1은 v7.6 기준 확정)

### 7-2. MVP 데이터 흐름

```
vworld geocode (VILLAGE.lat/lng 선행)
  → PUBLIC_DATA_SYNC_ORCHESTRATOR (cron·수동)
      → snap_population / snap_building / snap_statistics repository.ingest
      → snap_transport_repository.ingest_for_village (#6 2단계 + 15098534)
      → REGION.fiscal_self_reliance (연 1회)
  → tvi_score_repository.recalculate_all()
      → DISPATCH_RULE → prescription_result 생성
      → Gemini SSE (prescription-results/{id}/stream) + budget_estimate
  → 오케스트레이터 API (dashboard / village-detail / report-data)
      → Next.js 대시보드 → PDF 리포트 출력
```

### 7-3. MVP ERD 개요 — 18개 테이블

| 그룹 | 테이블 | 비고 |
|---|---|---|
| 공간/마을 | REGION, VILLAGE | REGION에 법정동코드·행정동코드·시군구코드·TAGO도시코드 4종 코드체계 + 재정자립도(연1회) 보유 |
| API 스냅샷 | SNAP_POPULATION, SNAP_BUILDING, SNAP_TRANSPORT, SNAP_STATISTICS | Repository ingest — Population(행안부 3종), Transport(**#6 + 15098534**, vworld 좌표 선행) |
| TVI 산출 | TVI_SCORE | risk_level·tvi_delta 역정규화 유지 |
| 처방 라이브러리 | PRESCRIPTION_TYPE, PRESCRIPTION_INDICATOR, PRESCRIPTION_FUND_SOURCE, DISPATCH_RULE, BUDGET_UNIT_PRICE | 1NF + O 원칙 |
| 처방 결과 | PRESCRIPTION_RESULT, BUDGET_ESTIMATE | D 원칙 — Gemini 설명은 `prescription_result_repository` 내부 |
| SaaS 운영 | ORGANIZATION, SUBSCRIPTION, USER, REPORT | 구독 티어 단일 출처 원칙 |

> 상세 스키마: `TownPulse_ERD_MVP_v6_1.md`.

### 7-4. MVP SOLID 적용 기준

| 원칙 | MVP 적용 여부 | 근거 |
|---|---|---|
| S — SNAP 테이블별 Repository ingest | ✅ 적용 | API 스펙 변경 시 마이그레이션 격리 |
| S — TVI 집계/계산 분리 | ✅ 적용 | `tvi_score_repository.recalculate_all()` |
| O — `IPrescriptionHandler` registry | ✅ 적용 | 처방 5종, 조건 분기 코드 없이 확장 가능 |
| L — `can_handle()` 선처리 | ✅ 적용 | null 반환·예외 없이 계약 일관성 보장 |
| I — Repository ingest 자가 등록 | ✅ 적용 | PUBLIC_DATA_SYNC가 순차·병렬 조율 |
| D — `prescription_result_port` / `IRepository` | ✅ 적용 | Gemini·NeonDB는 Repository·matrix 경유 |
| O — `ITviModel` 인터페이스 | ❌ 미적용 | 가중치 단일 버전, 오버엔지니어링 |
| O — `ISubscriptionPolicy` | ❌ 미적용 | 파일럿 단계, 티어 분기 없음 |
| I — `IReportDataProvider` CQRS | ❌ 미적용 | PDF 1종, 읽기 분리 불필요 |
| D — `IUnitPriceProvider` 캐시 | ❌ 미적용 | 단가 5종, 캐시 불필요 규모 |
| L — `confidence()` 폴백 | ❌ 미적용 | 단일 모델, XGBoost 없음 |

### 7-5. MVP 핵심 인터페이스 명세 (요약)

```python
# S — Repository ingest (테이블당 1 Repository, legal_dong_code / village 기준)
class SnapPopulationRepository:
    async def ingest(self, legal_dong_code: str) -> None: ...

class SnapTransportRepository:
    async def ingest_for_village(self, village_id: str) -> None:
        # vworld 좌표 필수 → BusRouteInfoInqireService 2단계 + 15098534

# S — TVI
class TviScoreRepository:
    async def recalculate_all(self) -> None: ...

# O + L — 처방 핸들러 registry
class IPrescriptionHandler(ABC):
    def can_handle(self, village: Village) -> bool: ...
    def execute(self, village: Village, tvi: TviScore) -> PrescriptionResult: ...

# D — Gemini는 prescription_result_repository 내부 (별도 AI adapter 파일 없음)
class PrescriptionResultRepository:
    async def stream_ai_description(self, result_id: str) -> AsyncIterator[str]: ...
    # Keymaker·Smith 경유 Gemini SSE
```

### 7-6. MVP 핵심 데모 시나리오

> 아래는 **제출 필수** 대표 예시(영춘면). 히트맵 228곳 전체 임의 클릭은 **[OPTIONAL]** — 백엔드 §12-1d.
>
> **TVI 설명 (심사·지자체):** 종합 TVI는 충북 **상대평가**입니다. 마을 원지표가 개선되어도 점수가 하락할 수 있으며, D-04에서 **5개 원지표 전월 대비**를 TVI와 함께 제시합니다 (§9-3-1). **증평군** 등 TAGO `cityCode` 미제공 시군은 「교통 데이터 제한적」 배지로 **확정 교통 공백과 구분**합니다 (백엔드 §9-4·프론트 §5-4).

> 1. 충북 히트맵에서 단양군 영춘면(`village_code=4300025000`) 클릭
> 2. 진단: "빈집 약 34% 추정, 버스 배차 180분, **최근접 정류장 1.2km(교통 공백)**, 고령화 61% → TVI 12점 (위험)"
> 3. AI 처방 (Gemini SSE로 1순위 처방 설명 실시간 생성):
>    - 1순위: 빈집 귀농인 임대주택 전환 / 예산 2.7~5.1억원 / TVI +8~12점 기대 / 기금 ✅
>    - 2순위: DRT 수요응답형 버스 도입 / 연 3,000~5,000만원 / TVI +4~6점 기대 / 기금 ✅
>    - 3순위: 귀농귀촌 인센티브 패키지 / 5,000만~1억원 / TVI +6~10점 기대 / 기금 ✅
> 4. "PDF 리포트 출력" → 담당자 보고서로 즉시 활용

---

## 8. 로드맵 — v1.0 (2027년)

> **충북 유료 구독 전환 단계**

### 8-1. v1.0 변경 동인

- 8종 API + 15098534 필드 검증 완료 (#1 건축HUB **요청·응답** probe 확정)
- KOSIS 시군구 빈집(`DT_1JU1512`)과 교차 검증으로 빈집 추정 정확도 향상
- 처방 라이브러리 10종으로 확장 (충북 행정 방향성 정렬)
- 충북 3~5개 시군 유료 구독 전환 → 구독 티어 정책 실제 작동
- TVI 가중치 전문가 델파이 기법 최적화 → TVI 모델 버전 관리 필요

### 8-2. v1.0 신규 기능

| 기능 | 상세 | 관련 테이블 |
|---|---|---|
| 빈집 공식 데이터 교차 검증 | KOSIS 시군구 빈집(`DT_1JU1512`) vs 추정 합산 | `VACANCY_VERIFICATION` 신설 |
| TVI 모델 버전 관리 | 델파이 가중치 도입 | `TVI_MODEL_VERSION` 신설 |
| 구독 정책 테이블화 | Basic/Standard/Premium 기능 분기 | `SUBSCRIPTION_POLICY` 신설 |
| 리포트 템플릿 관리 | PDF 외 웹 대시보드 리포트 | `REPORT_TEMPLATE` 신설 |
| 단가 캐시 레이어 | 처방 10종 캐시 성능 확보 | `UNIT_PRICE_CACHE` 신설 |
| 8종 API + 15098534 필드 정밀 검증 완료 | #1 건축HUB 요청·응답 Swagger 100% 확정 | 기존 SNAP_* Repository 보강 |

### 8-3. v1.0 ERD 변경 (MVP 대비 +5개 테이블 → 총 23개)

**신규 테이블**

| 테이블 | 역할 |
|---|---|
| `VACANCY_VERIFICATION` | 추정 빈집율 vs 공식 집계 편차 기록 |
| `TVI_MODEL_VERSION` | 모델 코드·가중치 설정·검증자·활성 여부 관리 |
| `SUBSCRIPTION_POLICY` | 티어별 기능 접근 권한 테이블화 |
| `REPORT_TEMPLATE` | 리포트 포맷·템플릿 URL 관리 |
| `UNIT_PRICE_CACHE` | 단가 캐시 만료 관리 |

**기존 테이블 변경**

| 테이블 | 변경 내용 |
|---|---|
| `TVI_SCORE` | `tvi_model_version_id FK` 추가 (string 대체) |
| `PRESCRIPTION_TYPE` | 5종 레코드 추가 (VILLAGE_CORP, VAC_DEMOLISH, ENTERPRISE, COMMERCE, WORKATION) |
| `SUBSCRIPTION` | `policy_id FK` 추가 → SUBSCRIPTION_POLICY 연결 |
| `REPORT` | `template_id FK` 추가, `report_type` 필드 추가 ("pdf" \| "dashboard") |

> v5.0에서 계획했던 `SNAP_BIZINFO`(cleaneye.go.kr)·`SNAP_REALESTATE`(reb.or.kr) 신설은 §3의 데이터 소스 로드맵 변경에 따라 v1.0 범위에서 제외되었습니다.

### 8-4. v1.0 SOLID 확장 적용

| 원칙 | v1.0 신규 적용 | 이유 |
|---|---|---|
| O | `ITviModel` 인터페이스 도입 | `WeightedSumModel` → `DelphiModel` 교체 |
| O | `ISubscriptionPolicy` 도입 | 티어별 기능 분기 실제화 |
| I | `IReportDataProvider` 분리 | 웹 대시보드 리포트 추가로 읽기 인터페이스 분리 필요 |
| D | `IUnitPriceProvider` 도입 | 단가 10종, 캐시 레이어 추가 가치 발생 |
| L | `confidence()` 준비 | 전문가 보정 모델 신뢰도 명시 필요 |

**v1.0 신규 인터페이스**

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

---

## 9. 로드맵 — v2.0 (2028년)

> **전국 확장 + ML 모델 고도화 단계**

### 9-1. v2.0 변경 동인

- 전국 시도 확장 → 지역별 커스텀 가중치 필요
- 실제 마을 소멸 사례 데이터로 ML 기반 가중치 학습 (XGBoost)
- 복합 처방 패키지 개념 도입 (처방 20종, 패키지 묶음)
- 충북·충남·강원 지자체 비교 분석(벤치마킹) 수요 발생
- API 수집 이력·오류 로그 관리 체계 필요

### 9-2. v2.0 신규 기능

| 기능 | 상세 | 관련 테이블 |
|---|---|---|
| 복합 처방 패키지 | "초위험 마을 패키지" 등 묶음 처방 | `PRESCRIPTION_PACKAGE`, `PACKAGE_ITEM` 신설 |
| ML 모델 학습 이력 | XGBoost 훈련 정확도·특성 중요도 기록 | `TVI_MODEL_TRAINING` 신설 |
| 어댑터 감사 로그 | 수집 성공/실패·재시도 이력 관리 | `ADAPTER_AUDIT_LOG` 신설 |
| 지자체 벤치마킹 | 타 읍면동·시군 TVI 비교 분석 | `REGION_BENCHMARK` 신설 |

### 9-3. v2.0 ERD 변경 (v1.0 대비 +5개 테이블 → 총 28개)

**신규 테이블**

| 테이블 | 역할 |
|---|---|
| `PRESCRIPTION_PACKAGE` | 복합 처방 패키지 정의 (target_risk_level 기반) |
| `PACKAGE_ITEM` | 패키지 내 처방 구성 및 적용 순서 |
| `TVI_MODEL_TRAINING` | ML 모델 훈련 샘플 수·정확도·특성 중요도 기록 |
| `ADAPTER_AUDIT_LOG` | 어댑터별 수집 상태·HTTP 상태코드·오류 메시지·재시도 횟수 |
| `REGION_BENCHMARK` | 마을 간 TVI 차이·벤치마킹 유형 기록 |

**기존 테이블 변경**

| 테이블 | 변경 내용 |
|---|---|
| `TVI_MODEL_VERSION` | `confidence_threshold` + `fallback_version_code` 필드 추가 |
| `PRESCRIPTION_RESULT` | `package_id FK (nullable)` 추가 — 패키지 처방 연결 |
| `DISPATCH_RULE` | `composite_operator (nullable)` + `linked_rule_id FK (nullable)` — 복합 조건 연결 |

### 9-4. v2.0 SOLID 확장 적용

| 원칙 | v2.0 신규 적용 | 이유 |
|---|---|---|
| L | `confidence()` 메서드 활성화 | XGBoost 데이터 부족 시 DelphiModel 폴백 필요 |
| O | `PackagePrescriptionHandler` 추가 | 복합 패키지 처방 신규 타입 |
| S | `AdapterAuditService` 분리 | 수집 이력·오류 로그 별도 책임 |
| D | `IRegionDataSource` 도입 | 지역별 커스텀 데이터 소스 추상화 |

**v2.0 신규 인터페이스**

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

## 10. 단계별 변화 요약

### 10-1. 테이블 수 변화

| 버전 | 시기 | 테이블 수 | 주요 추가 내용 |
|---|---|---|---|
| MVP | 2026 | 18개 | 기반 구조 전체 (SNAP_* 4개 분리, REGION 코드체계 4종, 처방 라이브러리 5종) |
| v1.0 | 2027 | 23개 | +5 (VACANCY_VERIFICATION, TVI_MODEL_VERSION, SUBSCRIPTION_POLICY, REPORT_TEMPLATE, UNIT_PRICE_CACHE) |
| v2.0 | 2028 | 28개 | +5 (PRESCRIPTION_PACKAGE, PACKAGE_ITEM, TVI_MODEL_TRAINING, ADAPTER_AUDIT_LOG, REGION_BENCHMARK) |

### 10-2. 처방 라이브러리 확장

| 버전 | 처방 종수 | 신규 처방 |
|---|---|---|
| MVP | 5종 | VAC_BUY, VAC_REMODEL, DRT, INCENTIVE, SOC_COMPLEX |
| v1.0 | 10종 | VILLAGE_CORP, VAC_DEMOLISH, ENTERPRISE, COMMERCE, WORKATION |
| v2.0 | 20종 | 복합 패키지 10종 추가 (PRESCRIPTION_PACKAGE 테이블로 관리) |

### 10-3. SOLID 적용 단계

| 원칙 | MVP | v1.0 | v2.0 |
|---|---|---|---|
| S — 어댑터 1:1 테이블 분리 | ✅ (5개) | ✅ | ✅ + AuditService |
| S — TVI 집계/계산 분리 | ✅ | ✅ | ✅ |
| O — `IPrescriptionHandler` registry | ✅ | ✅ | ✅ + PackageHandler |
| O — `ITviModel` 인터페이스 | ❌ | ✅ WeightedSum + Delphi | ✅ + XGBoost |
| O — `ISubscriptionPolicy` | ❌ | ✅ | ✅ |
| L — `can_handle()` | ✅ | ✅ | ✅ |
| L — `confidence()` | ❌ | 준비 | ✅ 활성화 |
| I — `IPublicDataAdapter` 자가 등록 | ✅ | ✅ | ✅ |
| I — `IReportDataProvider` | ❌ | ✅ | ✅ |
| D — `prescription_result_port` (Gemini) | ✅ (Gemini) | ✅ | ✅ |
| D — `IRepository` | ✅ | ✅ | ✅ |
| D — `IUnitPriceProvider` | ❌ | ✅ | ✅ |

### 10-4. 역정규화 유지 항목 (전 버전 공통)

| 컬럼 | 위치 | 유지 근거 |
|---|---|---|
| `risk_level` | `TVI_SCORE` | 히트맵 228개 읍면동 동시 렌더링 성능 |
| `tvi_delta` | `TVI_SCORE` | 전월 대비 등급 변화 알림 트리거 |
| `ai_description` | `PRESCRIPTION_RESULT` | Gemini API 재호출 비용 절감, 저장값 재사용 |

---

## 11. 비즈니스 모델

### 11-1. 메인 BM — 지자체 SaaS 구독 (B2G)

| 구독 티어 | 대상 | 월 구독료 | 포함 기능 | 적용 시기 |
|---|---|---|---|---|
| Basic | 군 단위 소규모 지자체 | 100만원 | 히트맵 + 기본 리포트 | v1.0 |
| Standard | 시 단위 지자체 | 200만원 | Basic + AI 처방 + 예산 시뮬레이션 | v1.0 |
| Premium | 광역시도 단위 | 500만원 | Standard + API 연동 + 전담 CS | v1.0 |

> MVP 파일럿 단계에서는 티어 분기 없이 무상 운영. v1.0에서 `SUBSCRIPTION_POLICY` 테이블 기반으로 정책 실제화.

### 11-2. 보조 BM

- **정부 용역 수주**: 지방소멸 대응 시스템 구축 사업 수주 (건당 5,000만~2억원)
- **데이터 리포트 판매**: 귀농귀촌 희망자, 연구기관 대상
- **컨설팅**: 지자체 행정 DX 컨설팅

### 11-3. 시장 규모

| 구분 | 규모 | 근거 |
|---|---|---|
| TAM | 약 1조원 | 전국 243개 지자체 스마트행정 시장 |
| SAM | 약 500억원 | 지방소멸 대응 행정 AI 특화 시장 |
| SOM | 약 15억원 | 충북·충남·강원 초기 3개 시도 (보수 추정) |

---

## 12. 5개년 성장 마일스톤

### 12-1. 연도별 목표

| 연도 | 단계 | 핵심 목표 | 서비스 버전 |
|---|---|---|---|
| 2026 | 씨앗 | 대회 수상 → 충북 2~3개 시군 무상 파일럿 MOU → 정부 창업지원금 확보 | MVP |
| 2027 | 발아 | 충북 3~5개 시군 유료 구독 전환 → 행안부 연계 용역 수주 1건 | v1.0 |
| 2028 | 성장 | 충북 전체 + 충남·강원 확장 → 국토부·행안부 전국 제안 | v2.0 |
| 2029 | 확장 | 전국 10개 이상 광역시도 계약 → 일본 시장 조사 착수 | v2.0+ |
| 2030 | 도약 | 국내 안정화 후 일본 파일럿 진입 → 동남아 시장 검토 | 해외 |

### 12-2. 매출 전망 — 3가지 시나리오

| 연도 | 보수 (기본값) | 중간 | 낙관 |
|---|---|---|---|
| 2026 | 0 (파일럿) | 0 (파일럿) | 0 (파일럿) |
| 2027 | 5,000만 (용역 1건) | 1.2억 (3개 시군) | 2.6억 (11개 시군) |
| 2028 | 3억 (충북+1개 시도) | 7억 | 12억 |
| 2029 | 8억 (국내 확장) | 20억 | 45억 |
| 2030 | 15억 (국내 안정화) | 40억 | 100억+ |

### 12-3. 단계별 KPI

| KPI | 2026 (MVP) | 2027 (v1.0) | 2028 (v2.0) | 2029 | 2030 |
|---|---|---|---|---|---|
| 구독 지자체 수 | 0 (파일럿) | 3~5개 | 15개 | 40개 | 60개+ |
| 월 활성 사용자 | 베타 10명 | 100명 | 500명 | 2,000명 | 5,000명 |
| 분석 마을 수 | 충북 228개 | 충북 전체 | 3개 시도 | 전국 | 전국 |
| 처방 라이브러리 | 5종 | 10종 | 20종 | 30종+ | 30종+ |
| 연동 API 수 | 8종 + 15098534 (probe 대부분 확정) | 8종+15098534 (필드 100%) | 확장 | 확장 | 확장 |
| 백엔드 도메인 | 22개 (18+오케스트4) | 22+ | — | — | — |
| ERD 테이블 수 | 18개 | 23개 | 28개 | — | — |
| 해외 진출 | — | — | — | 일본 시장조사 | 일본 파일럿 |

---

## 13. 해외 진출 전략 — 일본 (2029년 이후)

> 원칙: 한국 시장 안정화 우선. 일본은 2029년 시장 조사 착수, 2030년 파일럿 진입.

**일본 진출 배경**
- 일본 전체 1,718개 시정촌 중 절반 이상이 소멸위험 (한국보다 10~20년 앞서 진행)
- 일본 정부 지방소멸 대응 예산 연 1조엔(약 9조원) 규모
- 2021년 디지털청 신설 후 지자체 DX 의무화 추진 중

| 시기 | 단계 | 내용 |
|---|---|---|
| 2029년 | 시장 조사 | JETRO 프로그램 활용, 아키타·시마네 등 소멸 심각 지역 현지 조사 |
| 2030년 | 파일럿 | 일본 1~2개 지자체 소규모 파일럿 (NTT데이터 등 SI 파트너 협의) |
| 2031년~ | 확장 | 화이트라벨 파트너십으로 확산 |

---

## 14. ESG 혁신 가치

| ESG 항목 | TownPulse의 기여 |
|---|---|
| 상생협력 (S) | 지자체·주민·귀농인·소상공인이 함께 활용하는 개방형 플랫폼 |
| 일자리 창출 (S) | 빈집 정비·귀농귀촌 유치로 농촌 일자리 간접 창출 |
| 탄소중립 (E) | 버스 노선 최적화로 불필요한 공차 운행 감소 |
| 윤리경영 (G) | 공공데이터 기반 투명한 행정 의사결정 지원 |
| 디지털 격차 해소 (S) | 농촌 교통·행정 취약계층의 접근성 개선 |

---

## 15. 팀 구성

| 역할 | 담당 업무 | 기술스택 |
|---|---|---|
| AI 엔지니어 (1명) | 공공API 파이프라인·TVI 예측 모델·처방 매핑 로직 | Python, scikit-learn, XGBoost |
| 백엔드 개발 (1명) | API 서버·DB 설계·Gemini 연동·예산 계산 엔진 | FastAPI, NeonDB, Google GenAI SDK, AWS EC2 |
| 프론트엔드 개발 (1명) | 지도 대시보드·예산 시뮬레이션 UI·PDF·테마 | Next.js 14, TypeScript, Tailwind, Leaflet, Recharts, next-themes, Zustand |

---

## 16. 경쟁우위 및 평가항목 대응

### 16-1. 차별성 요약

| 구분 | 기존 시스템 | 내마을AI | TownPulse |
|---|---|---|---|
| 사용자 | 행정 담당자 (엑셀) | 귀촌 희망자 | 행정 담당자 (AI 보조) |
| 분석 방식 | 수작업 현황 파악 | 이주 정보 안내 | AI 예측 + 처방 + 예산 시뮬레이션 |
| 커버 범위 | 개별 부서 | 제천시 | 충북 전체 |
| 예산 근거 | 담당자 경험 의존 | 해당 없음 | 국토부·행안부 단가 라이브러리 기반 |
| 지수 근거 | 없음 | 없음 | 행안부 체계 + 전문가 검증 예정 |

### 16-2. 평가항목별 대응 전략

| 평가항목 | 배점 | 대응 포인트 |
|---|---|---|
| 공공데이터 활용 | 25점 | 8종 API + 15098534 probe 실연동·법정동코드 JOIN·교통 정류장 접근성 지표 |
| AI 혁신성 | 20점 | TVI 복합지수 + Gemini 처방 설명(SSE) + 정부 단가 라이브러리 결합 |
| 독창성 | 15점 | 빈집·인구·교통(노선+정류장) 악순환 통합 + 예산 시뮬레이션 원스톱 |
| 완성도 | 15점 | 라이브 데모 + Hexagonal 22도메인·22×12 프랙탈 + PDF 즉시 출력 |
| 발전 가능성 | 20점 | 보수적 매출 시나리오 + v1.0/v2.0 단계별 확장 계획 + 국내 안정화 후 일본 |
| ESG 혁신 | 5점 | 상생·일자리·탄소중립 자연스럽게 충족 |

---

## 변경 이력

| 버전 | 주요 변경 내용 |
|---|---|
| v0.1 | 최초 작성 |
| v0.2 | 내마을AI 차별성 명시 / TVI 행안부 레퍼런스 추가 / Gemini 전환 / 매출 보수화 / 일본 2029년으로 조정 |
| v0.3 | 예산 시뮬레이션 구조 신설 / Gemini 역할 명확화 (텍스트 vs 숫자 분리) / 데모 시나리오 예산 수치 반영 |
| v0.4 | 빈집 비율 산출 방식 명시 / 처방 라이브러리 v1.0 추가 5종 충북 행정 정렬 / MVP 완성도 현실화 (5개 실연동) |
| v5.0 | MVP / v1.0 / v2.0 단계 구분 명시 / ERD 정규화·SOLID 설계 결정 통합 / 처방 라이브러리 코드(VILLAGE_CORP 등) 명시 / 단계별 테이블 수·KPI·인터페이스 명세 통합 / 구독 티어 적용 시기 명시 |
| v6.0 | 공공데이터 9개 API 승인·Claude 전환(후속 v7에서 정정)·ERD 18테이블·인프라 확정 |
| v7.0 | **8종 API + 15098534 MVP** (TAGO #7 삭제·#6 통합) · **probe 확정**(#2~#4·#6·15098534, #1 요청만 ⚠️) · **Gemini API** 확정(v6 Claude 기술서 정정) · **SNAP_TRANSPORT 정류장 접근성** · **22도메인**(PUBLIC_DATA_SYNC 오케스트 추가) · Repository ingest·matrix 7파일 · SSOT 문서 링크(ERD v5·백엔드 v8·프론트 v2) · 데모·평가·KPI 정합 |
| v7.1 | **`birth_rate`/`daytime_population` → REGION**(KOSIS #8·시군구·MVP TVI 미사용) · 건축HUB 요청 파라미터 ✅ · v1.0 `VACANCY_VERIFICATION`→KOSIS `DT_1JU1512` · ERD v5.1·백엔드 v8.4 정합 |
| v7.2 | **TVI §9 정합** — `pop_decline_score` 5지표 min-max · 행안부 **항목** 준용(산식 자체 설계) · 처방 TVI `simulate_tvi_gain()` 역산 명시 |
| v7.3 | **§9-0 TVI 경계** — min-max는 `pop_decline_score`만 · 빈집·교통 §9-4 선형식 · DRT=배차만 — 백엔드 v8.8 정합 |
| v7.4 | **§10-9 정류장 1km** — 15098534+노선카탈로그 Haversine · 시/군 `_city_cache` · `tago_route_counts_chungbuk.json` (1,679노선) — 백엔드 v8.9 |
| v7.5 | **§10-8b 주거용 화이트리스트** — 7종(다중주택 추가)·기숙사 제외 확정 · unmatched 감사 로깅 — 백엔드 v8.10 · ERD v5.3 |
| v7.6 | **§10-8-1 `net_youth_migration`** — 시/도 17개 스윕 · 3일 분할 배치 · **제출 06-26** — 백엔드 v9.0 · ERD v6.0 |
| v7.7 | **§12-1c USER 로그인·QA 시드** — `password_hash` · `seed_qa_account.py` · AUTH 도메인 없음 — 백엔드 v9.1 · ERD v6.1 |
| v7.8 | **§12-1d [OPTIONAL] 228처방 선생성** · Railway 배포 · 프론트 §13 403 폴백 — 백엔드 v9.2 · 프론트 v2.2 |
| v7.9 | **§9-3-1 TVI 상대평가 한계·`tvi_delta` 해석** — EMA는 MVP이후 v4_0 §1-1 — 백엔드 v9.3 |
| v7.10 | **§7-6 증평군 교통 왜곡 수정** — `tago_city_code` NULL 시 GPS 유지·`bus_route_count=null`·배지 분리 — 백엔드 v9.4 · 프론트 v2.3 · MVP이후 v4_0 §1-5 |
| v7.11 | **§4-4 §9-5 처방 시뮬 SNAP 연동** — INCENTIVE γ(교통·청년) · SOC 빈집 연계 — 백엔드 v9.5 · 재정 UI·Delphi는 v4_0 §1-6 이월 |

---

*© 2026 Pulse Lab | TownPulse 사업정의서 v7.11 | Confidential*
