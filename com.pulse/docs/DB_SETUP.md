# TownPulse DB 설정

## Fresh DB

```bash
cd com.pulse
# .env 에 DATABASE_URL, JWT_SECRET 설정
alembic upgrade head
python -c "
import asyncio
from core.matrix.grid_oracle_database_manager import get_session_factory
from apps.townpulse.adapter.outbound.repositories.db_init import init_data

async def main():
    async with get_session_factory()() as s:
        await init_data(s)
        await s.commit()
asyncio.run(main())
"
```

## 환경 변수

| 변수 | 기본 | 설명 |
|------|------|------|
| `SEED_MOCK_SNAPS` | `0` | `1`이면 합성 SNAP/TVI 시드 (로컬 빠른 데모) |
| `ALLOW_CREATE_ALL_FALLBACK` | `1` | Alembic 실패 시 `create_all` 폴백 |

## 실데이터 동기화

공공API 키 설정 후:

```powershell
python scripts/validate_env_keys.py
python scripts/run_full_sync.py
```

또는 QA 로그인 후 `POST /api/townpulse/admin/sync/trigger` → migration-chunk 0~2 → finalize.

## Alembic

```bash
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
alembic downgrade -1
```
