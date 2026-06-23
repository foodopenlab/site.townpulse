from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.townpulse.adapter.inbound.api import townpulse_router
from apps.townpulse.adapter.outbound.repositories.db_init import (
    apply_real_village_names,
    apply_village_coordinates,
    ensure_demo_prescriptions,
    ensure_mvp_qa_credentials,
    init_data,
    init_schema,
)
from apps.townpulse.dependencies.public_data_sync_orchestrator_provider import register_batch_jobs, scheduler
from core.matrix.grid_keymaker_secret_manager import get_keymaker
from core.matrix.grid_oracle_database_manager import dispose_engine, get_session_factory
from sqlalchemy import text


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_keymaker().load_env()
    await init_schema()
    factory = get_session_factory()
    async with factory() as session:
        count = await session.scalar(text("SELECT COUNT(*) FROM village"))
        if not count or count != 228:
            if not os.getenv("SEED_MOCK_SNAPS"):
                os.environ["SEED_MOCK_SNAPS"] = "1"
            await init_data(session)
        await ensure_demo_prescriptions(session)
        await ensure_mvp_qa_credentials(session)
        await apply_real_village_names(session)
        await apply_village_coordinates(session)
        await session.commit()
    register_batch_jobs()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)
    await dispose_engine()


app = FastAPI(title="TownPulse API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://townpulse.site"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(townpulse_router, prefix="/api")


if __name__ == "__main__":
    import os
    import sys

    import uvicorn

    # Windows + reload=True 시 reloader/자식 프로세스가 포트를 중복 점유해 HTTP 무응답이 날 수 있음.
    use_reload = os.getenv("UVICORN_RELOAD", "").lower() in ("1", "true", "yes")
    if sys.platform == "win32" and use_reload:
        print("경고: Windows에서는 UVICORN_RELOAD=1 없이 reload를 켜지 않습니다. 좀비 프로세스 방지.")
        use_reload = False

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=use_reload,
    )
