# TownPulse — CLAUDE.md 개발 가이드

이 문서는 TownPulse 프로젝트의 빌드, 테스트, 실행 명령어 및 Titanic 프랙탈 아키텍처 코딩 가이드라인을 정의합니다.

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

### Titanic Fractal Architecture (11-File Set)
도메인 컴포넌트 `{name}` 추가 시 반드시 아래의 11개 구성 요소 파일을 1:1로 매칭하여 작성해야 합니다.

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

### 경계 톨게이트 (Boundary Gate) 및 타입 변환 규칙
- **Inbound 톨게이트:** Router ↔ Interactor(UseCase) 경계에서 `mapper`를 통해 HTTP Request/Response `schema`와 비즈니스 `dto` 또는 `entity` 타입을 상호 변환합니다. Interactor에 `schema` 타입을 직접 전달해서는 안 됩니다.
- **Outbound 톨게이트:** Repository ↔ Database 경계에서 `orm_mapper`를 통해 비즈니스 `entity`와 SQLAlchemy `orm` 모델을 상호 변환합니다.
- **도메인 순수성 유지:** `domain/` 및 `app/use_cases/` 레이어에서는 FastAPI, SQLAlchemy, httpx 등 외부 프레임워크나 라이브러리를 직접 import하여 사용할 수 없습니다.

### 인프라 및 핵심 원칙
- **NeonDB 연결:** `sslmode=require`를 필수로 사용하여 비동기 연결(`asyncpg`)을 구성합니다. DB 연결 및 트랜잭션 관리는 `core/matrix/grid_oracle_database_manager.py` (Oracle) 단일 진입점을 통해서만 수행합니다.
- **비밀키 및 API 설정:** `core/matrix/grid_keymaker_secret_manager.py` (Keymaker) 단일 진입점을 통해 모든 비밀 값(API_KEY, JWT_SECRET 등)을 로드하며, 개별 파일에서 `os.getenv`를 직접 호출해서는 안 됩니다.
- **인증 및 Depends 가드:** JWT 처리 및 권한 가드는 `core/matrix/grid_trinity_hacker_mixin.py` (Trinity)를 통해 관리합니다.
- **단일 책임 원칙 (SRP):** 하나의 API Router는 하나의 ERD 테이블을 담당해야 합니다.
