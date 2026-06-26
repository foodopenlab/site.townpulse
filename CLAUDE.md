# TownPulse — CLAUDE.md 개발 가이드

이 문서는 Karpathy의 행동 지침(Core Behavioral Guidelines)을 최우선으로 적용하며, TownPulse 프로젝트의 빌드, 실행 명령어 및 TownPulse 고유 아키텍처 가이드라인을 정의합니다.


---

## 0. Core Behavioral Guidelines (최우선 행동 지침)

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.
- **[필수 지침]** 코드를 직접 수정하기 전에, 반드시 답변 또는 구현 계획을 세워 사용자에게 보고하고 **명시적인 승인이나 허락을 받은 후에만** 코드 수정을 개시하십시오. 승인 전에는 어떠한 코드 변경도 시도하지 않습니다.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
*Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.*

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.
When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.
*The test: Every changed line should trace directly to the user's request.*

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
*Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.*

---

## 1. 프로젝트 실행 및 개발 명령어

### 백엔드 (com.pulse)
- **의존성 설치:** `pip install -r requirements.txt`
- **로컬 서버 실행:** `python main.py` (또는 `env UVICORN_RELOAD=true python main.py` - Windows에서는 reload 경고 확인 필요)
- **DB 마이그레이션 (Alembic):**
  - **마이그레이션 생성:** `alembic revision --autogenerate -m "작업내용"`
  - **마이그레이션 적용:** `alembic upgrade head`
- **테스트 스크립트 실행:** `python scripts/test_energy_api.py`

### 프론트엔드 (town.www)
- **의존성 설치:** `npm install`
- **로컬 개발 서버 실행:** `npm run dev`
- **프로덕션 빌드:** `npm run build`
- **린트 및 포맷팅:** `npm run lint`

---

## 2. 프로젝트 아키텍처 및 코딩 가이드라인

### 아키텍처 패러다임 및 AI 하네스 엔지니어링
- 본 프로젝트는 **모듈러 모놀리스(Modular Monolith)** 구조 하에 **헥사고날 아키텍처(Hexagonal, Ports & Adapters) + 클린 아키텍처(Clean) + DDD(Domain-Driven Design)** 모델을 전면 채택합니다.
- 이는 **AI를 통한 테스트 하네스 엔지니어링(Harness Engineering) 및 자동화**를 극대화하기 위함입니다. 따라서 규격화된 프랙탈 구조를 엄격히 보존해야 합니다.

### TownPulse Fractal Architecture (11-File Set)
도메인 컴포넌트 `{name}` 추가 시 반드시 아래의 11개 구성 요소 파일을 1:1로 매칭하여 작성해야 합니다. (단, **Value Object 예외** 조항 참고)


1. **router:** `apps/townpulse/adapter/inbound/api/v1/{name}_router.py`
2. **use_case:** `apps/townpulse/app/ports/input/{name}_use_case.py`
3. **interactor:** `apps/townpulse/app/use_cases/{name}_interactor.py`
4. **port:** `apps/townpulse/app/ports/output/{name}_port.py`
5. **repository:** `apps/townpulse/adapter/outbound/repositories/{name}_repository.py`
6. **schema:** `apps/townpulse/adapter/inbound/api/schemas/{name}_schema.py`
7. **dto:** `apps/townpulse/app/dtos/{name}_dto.py`
8. **orm:** `apps/townpulse/adapter/outbound/orm/{name}_orm.py`
9. **entity:** `apps/townpulse/domain/entities/{name}_entity.py`
10. **mapper:** `apps/townpulse/adapter/inbound/mappers/{name}_mapper.py`
11. **orm_mapper:** `apps/townpulse/adapter/outbound/orm_mappers/{name}_orm_mapper.py`

### ⚠️ Value Object (VO) 예외 및 AOP 관점 적용
- **VO 프랙탈 제외 규칙**: DDD 설계 상 도메인의 **Value Object(VO)**만큼은 횡단 관심사(Cross-cutting Concern)로서 공통 재사용할 수 있도록 **AOP(Aspect-Oriented) 관점**으로 다룹니다.
- 따라서 VO는 11-File Set 프랙탈 구조의 제약을 받지 않고 `domain/value_objects/` 경로 하위에서 자유롭게 공통 모듈로 설계 및 공유가 허용되는 유일한 예외 영역입니다.

### 경계 톨게이트 (Boundary Gate) 및 타입 변환 규칙
- **Inbound 톨게이트:** Router ↔ Interactor(UseCase) 경계에서 `mapper`를 통해 HTTP Request/Response `schema`와 비즈니스 `dto` 또는 `entity` 타입을 상호 변환합니다. Interactor에 `schema` 타입을 직접 전달해서는 안 됩니다.
- **Outbound 톨게이트:** Repository ↔ Database 경계에서 `orm_mapper`를 통해 비즈니스 `entity`와 SQLAlchemy `orm` 모델을 상호 변환합니다.
- **도메인 순수성 유지:** `domain/` 및 `app/use_cases/` 레이어에서는 FastAPI, SQLAlchemy, httpx 등 외부 프레임워크나 라이브러리를 직접 import하여 사용할 수 없습니다.

### 인프라 및 핵심 원칙
- **NeonDB 연결:** `sslmode=require`를 필수로 사용하여 비동기 연결(`asyncpg`)을 구성합니다. DB 연결 및 트랜잭션 관리는 `core/matrix/grid_oracle_database_manager.py` (Oracle) 단일 진입점을 통해서만 수행합니다.
- **비밀키 및 API 설정:** `core/matrix/grid_keymaker_secret_manager.py` (Keymaker) 단일 진입점을 통해 모든 비밀 값(API_KEY, JWT_SECRET 등)을 로드하며, 개별 파일에서 `os.getenv`를 직접 호출해서는 안 됩니다.
- **인증 및 Depends 가드:** JWT 처리 및 권한 가드는 `core/matrix/grid_trinity_hacker_mixin.py` (Trinity)를 통해 관리합니다.
- **단일 책임 원칙 (SRP):** 하나의 API Router는 하나의 ERD 테이블을 담당해야 합니다.
- **공공 API 호출 캐싱 및 최적화 규칙:**
  1. **상위 행정구역 단위 캐싱 (Sigungu-level Caching):** 공공 API 연동 시 마을별로 API를 개별 호출하여 발생하는 속도 저하 및 API 쿼타 낭비를 방지하기 위해, 가능한 한 상위 행정구역(시군구/도시 등) 단위의 전체 데이터를 1회 통합 조회하고 이를 메모리에 캐시하여 사용해야 합니다. (예: 주민등록인구 수집 시 10자리 법정동코드 대신 5자리 시군구코드로 API를 호출하여 동일 시군구 내의 타 마을들은 캐시에서 처리)
  2. **비동기 병렬 호출 (`asyncio.gather` & `Semaphore`):** 주택별/건물별 단독 조회가 불가피한 API(예: 전기 사용량 등)의 경우 `asyncio.gather` 및 `asyncio.Semaphore(15)`를 활용해 동시 호출 수를 제어하며 비동기 병렬로 가속 호출해야 합니다.
  3. **중복 호출 원천 차단 (Monthly Snapshot Skip):** 당월(또는 기준연월)의 스냅샷 데이터가 이미 로컬 DB에 존재하고 정상 적재 완료 상태라면, 공공 API 호출 자체를 완전히 건너뛰도록(Skip) 중복 조회 차단 필터를 필히 적용하여 중복 쿼타 낭비를 방지하고 즉시 완료되도록 합니다.
- **백엔드 작업 진행 현황 보고 규칙:** 대량의 데이터를 적재, 연산, 동기화하거나 시간이 다소 소요되는 백엔드 배치 및 시드 스크립트 실행 시에는 진행률(%)이나 작업 단계를 터미널 및 사용자 피드백으로 중간 중간 지속 보고(print, logger 등)하여 진행 과정을 투명하게 확인할 수 있도록 설계해야 합니다.
- **⚠️ 읍면동(EMD) 단일화 및 마을 수 동기화 규칙 (방안 B):**
  1. **마을 단위 기준**: 모든 수집 및 분석 지표는 법정동 중 "리" 단위를 배제하고 "읍", "면", "동" 단위만 집계하는 방안 B를 따릅니다.
  2. **마을 수 동기화 (Single Source of Truth)**: 충북 전체 분석 마을 수는 기존 135개에서 "리" 단위가 배제되면서 **107개**로 통일되었습니다.
  3. **프론트엔드 상수**: `town.www/lib/config/constants.ts` 의 `TOTAL_VILLAGE_COUNT` 값을 `107`로 일치시킵니다.
  4. **백엔드 집계**: `com.pulse`의 모든 대시보드 요약 및 맵 데이터 쿼리(예: `fetch_summary()`, `fetch_map_villages()`)는 `~VillageOrm.name.like("%리")` 조건을 적용해 107개 활성 EMD만 집계되도록 강제해야 합니다.

---

## 3. 데이터베이스 정규화 및 역정규화 설계 원칙
- **마스터 데이터의 3NF(제3정규형) 준수**: 외부 인프라 시설(병원, 약국, 초등학교, 상가 등)의 고유 정보(이름, 주소, 경위도 좌표 등)는 중복 저장을 방지하기 위해 반드시 독립된 마스터 테이블(예: `infrastructure_facility`)로 설계하여 3NF를 충족해야 합니다.
- **스냅샷 역정규화 및 성능 최적화**: 실시간 조회 성능 최적화와 시점별 이력 보존을 위해, 각 마을(village) 단위로 연산된 최종 거리 수치 및 인덱스 결과는 스냅샷 테이블(예: `snap_infrastructure`)에 직접 컬럼으로 기록합니다.
- **스냅샷 오염 방지**: 스냅샷 테이블 내에 시설 마스터의 텍스트 정보(상호명, 상세주소 등)를 중복으로 저장하는 무분별한 역정규화는 절대 금지합니다. 오직 연산된 수치(정수/실수)와 외래키(FK)만 관리해야 합니다.
