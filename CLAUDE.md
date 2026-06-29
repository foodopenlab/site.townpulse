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
- "Fix the bug" → "재현 조건 확인 → 코드 수정 → 동일 조건으로 재실행하여 정상 확인"
- "Add feature" → "어떤 입력에서 어떤 출력이 나와야 하는지 먼저 명시 → 구현 → 검증"
- "Refactor X" → "수정 전후 동작이 동일한지 스크립트/로그로 확인"
For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```
*이 프로젝트는 별도 pytest 테스트 스위트가 없으므로, 검증은 실행 스크립트 출력 및 DB 조회로 대체한다.*

---

## 1. 프로젝트 실행 및 개발 명령어

### 백엔드 (com.pulse)
- **의존성 설치:** `pip install -r requirements.txt`
- **로컬 서버 실행:** `python main.py` (또는 Windows PowerShell: `$env:UVICORN_RELOAD="true"; python main.py`)
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
  2. **비동기 병렬 호출 (`asyncio.gather` & `Semaphore`):** 주택별/건물별 단독 조회가 불가피한 API(예: 전기 사용량 등)의 경우 `asyncio.gather` 및 `asyncio.Semaphore`를 활용해 동시 호출 수를 제어하며 비동기 병렬로 가속 호출해야 합니다. Semaphore 값은 API 특성에 따라 레포지토리별로 결정하며 CLAUDE.md에 특정 숫자를 고정하지 않습니다.
  3. **중복 호출 원천 차단 (Monthly Snapshot Skip):** 당월(또는 기준연월)의 스냅샷 데이터가 이미 로컬 DB에 존재하고 정상 적재 완료 상태라면, 공공 API 호출 자체를 완전히 건너뛰도록(Skip) 중복 조회 차단 필터를 필히 적용하여 중복 쿼타 낭비를 방지하고 즉시 완료되도록 합니다.
- **⚠️ SQLAlchemy AsyncSession 동시성 안전 규칙:**
  - `asyncio.gather`로 여러 코루틴이 하나의 `AsyncSession`을 공유할 때, SELECT 쿼리는 반드시 `with self._session.no_autoflush:` 블록 안에서 실행해야 합니다. 그렇지 않으면 pending add 객체들이 자동 flush를 트리거하여 `Session is already flushing` 또는 `DeadlockDetectedError`가 발생합니다.
  - 레포지토리 내에서 `await self._session.flush()`를 직접 호출하는 것을 금지합니다. commit은 상위 호출자(스크립트 또는 인터랙터)가 일괄 처리합니다.
  - **유일한 예외:** `public_data_sync_orchestrator_repository.py`처럼 DB 생성 ID를 즉시 반환해야 하는 단일(비동시) 호출에서는 `flush()` 후 `commit()` 패턴이 허용됩니다.
- **⚠️ 실 API 실패 시 가짜 데이터 삽입 금지:**
  - 공공 API 호출 실패 시 `hashlib` 또는 임의 계산값으로 생성한 가짜 데이터를 DB에 삽입하는 패턴을 금지합니다.
  - 실패 시에는 `logger.warning`으로 기록 후 `return`으로 스킵합니다. 가짜 데이터가 실데이터처럼 취급되는 오염을 방지합니다.
  - **예외:** 실 API 자체가 존재하지 않는 필드(예: `kosis_vacancy_rate`, `disaster_risk_ratio`)는 대체 계산값 사용이 허용되며, 해당 필드 옆에 "실API 없음" 주석을 명시합니다.
- **⚠️ 에너지 API 쿼타 제약:**
  - 에너지 수집 스크립트(`run_energy_ingest_resume.py`)의 `MONTHS_PER_RUN`은 **최대 1**로 유지합니다.
  - 에너지 API(ENERGY_ELCTY_URL)와 건물목록 API(BUILDING_HUB_TITLE_URL)가 동일 쿼타(10,000회/일)를 공유하며, 1개월 처리 시 실 호출량은 약 5,355회(에너지 4,590 + 건물목록 765)입니다. 2개월 시 10,710회로 쿼타를 초과합니다.
- **백엔드 작업 진행 현황 보고 규칙:** 대량의 데이터를 적재, 연산, 동기화하거나 시간이 다소 소요되는 백엔드 배치 및 시드 스크립트 실행 시에는 진행률(%)이나 작업 단계를 터미널 및 사용자 피드백으로 중간 중간 지속 보고(print, logger 등)하여 진행 과정을 투명하게 확인할 수 있도록 설계해야 합니다.
- **⚠️ 읍면동(EMD) 단일화 및 마을 수 동기화 규칙 (방안 B):**
  1. **마을 단위 기준**: 모든 수집 및 분석 지표는 법정동 중 "리" 단위를 배제하고 "읍", "면", "동" 단위만 집계하는 방안 B를 따릅니다.
  2. **마을 수 동기화 (Single Source of Truth)**: 충북 전체 분석 마을 수는 `chungbuk_emd_data.py` 기준 **153개 읍면동**으로 통일되었습니다. (DB 시드 153개 전부 읍·면·동이며 "리" 항목 없음)
  3. **프론트엔드 상수**: `town.www/lib/config/constants.ts` 의 `TOTAL_VILLAGE_COUNT` 값을 `153`으로 일치시킵니다.
  4. **백엔드 집계**: `com.pulse`의 모든 대시보드 요약 및 맵 데이터 쿼리(예: `fetch_summary()`, `fetch_map_villages()`)는 `~VillageOrm.name.like("%리")` 조건을 안전 가드로 유지하되, 현재 DB 기준 153개 활성 EMD가 집계됩니다.

---

## 3. 점검일지 기록 규칙 (의무)

**점검일지 경로:** `vault/backend/점검.md`

아래 작업을 수행한 후에는 반드시 점검일지에 기록을 남겨야 합니다.

### 기록 대상
- **버그 수정**: 발생 원인, 수정 파일, 수정 내용 요약
- **코드 변경**: 어떤 파일을 왜 수정했는지 (기능 추가, 리팩터링, 패턴 교정 등)
- **스크립트 추가/삭제**: 파일명과 이유
- **API/쿼타 변경**: 호출량 추정치, 기본값 변경
- **데이터 수집 완료**: 영역, 마을 수, 소요 시간
- **아키텍처 의사결정**: 설계 변경 사항 및 근거

### 기록 형식
점검일지의 **개정이력** 섹션에 한 줄 요약을 추가하고, 해당 섹션 표/목록을 업데이트합니다.

```
* **YYYY-MM-DD (vX.Y)**: [작업 내용 한 줄 요약]. [수정 파일 수 또는 핵심 변경사항].
```

### 예외
- 단순 오타 수정, 주석 수정, 문서만 변경한 경우는 생략 가능.
- 단, 아키텍처·데이터 수집·버그 수정은 예외 없이 기록.

---

## 4. 데이터베이스 정규화 및 역정규화 설계 원칙
- **마스터 데이터의 3NF(제3정규형) 준수**: 외부 인프라 시설(병원, 약국, 초등학교, 상가 등)의 고유 정보(이름, 주소, 경위도 좌표 등)는 중복 저장을 방지하기 위해 반드시 독립된 마스터 테이블(예: `infrastructure_facility`)로 설계하여 3NF를 충족해야 합니다.
- **스냅샷 역정규화 및 성능 최적화**: 실시간 조회 성능 최적화와 시점별 이력 보존을 위해, 각 마을(village) 단위로 연산된 최종 거리 수치 및 인덱스 결과는 스냅샷 테이블(예: `snap_infrastructure`)에 직접 컬럼으로 기록합니다.
- **스냅샷 오염 방지**: 스냅샷 테이블 내에 시설 마스터의 텍스트 정보(상호명, 상세주소 등)를 중복으로 저장하는 무분별한 역정규화는 절대 금지합니다. 오직 연산된 수치(정수/실수)와 외래키(FK)만 관리해야 합니다.
