"""DB 초기화 — Alembic 마이그레이션 + 마스터 시드."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import PrescriptionResultOrm, UserOrm, VillageOrm
from apps.townpulse.adapter.outbound.repositories.db_seed import seed_database
from apps.townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository
from apps.townpulse.services.seed_data import (
    DEMO_VILLAGE_CODE,
    MVP_QA_ORG_UUID,
    MVP_QA_PASSWORD,
    generate_village_rows,
)
from apps.townpulse.services.chungbuk_village_names import is_placeholder_village_name
from core.matrix.grid_neo_theone_base import NeoBase
from core.matrix.grid_oracle_database_manager import get_engine

logger = logging.getLogger(__name__)


def _run_alembic_upgrade() -> None:
    from alembic import command
    from alembic.config import Config

    root = Path(__file__).resolve().parents[5]
    cfg = Config(str(root / "alembic.ini"))
    command.upgrade(cfg, "head")


async def init_schema() -> None:
    """Alembic upgrade head. 실패 시 create_all 폴백(로컬 개발)."""
    try:
        _run_alembic_upgrade()
        return
    except Exception as exc:
        logger.warning("Alembic upgrade 실패 — create_all 폴백: %s", exc)
        if os.getenv("ALLOW_CREATE_ALL_FALLBACK", "1").lower() not in ("0", "false", "no"):
            engine = get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(NeoBase.metadata.create_all)
        else:
            raise


async def init_data(session: AsyncSession) -> None:
    await seed_database(session)


async def apply_real_village_names(session: AsyncSession) -> int:
    """기존 Neon DB의 목업 마을명(충주시읍면동10 등)을 실명으로 갱신."""
    code_to_name = {row["emd_code"]: row["name"] for row in generate_village_rows(228)}
    villages = (await session.execute(select(VillageOrm))).scalars().all()
    updated = 0
    for village in villages:
        if not village.emd_code:
            continue
        new_name = code_to_name.get(village.emd_code)
        if not new_name:
            continue
        if village.name != new_name and is_placeholder_village_name(village.name):
            village.name = new_name
            updated += 1
    return updated


async def apply_village_coordinates(session: AsyncSession) -> int:
    """시드 좌표를 DB에 반영 — 구버전 대각선 배치 좌표 보정."""
    code_to_coords = {row["emd_code"]: (row["lat"], row["lng"]) for row in generate_village_rows(228)}
    villages = (await session.execute(select(VillageOrm))).scalars().all()
    updated = 0
    for village in villages:
        if not village.emd_code:
            continue
        coords = code_to_coords.get(village.emd_code)
        if not coords:
            continue
        lat, lng = coords
        if village.lat != lat or village.lng != lng:
            village.lat = lat
            village.lng = lng
            updated += 1
    return updated


async def ensure_demo_prescriptions(session: AsyncSession) -> None:
    """데모 마을 처방이 없으면 선생성 — demo_readonly는 POST 불가."""
    demo = (
        await session.execute(select(VillageOrm).where(VillageOrm.emd_code == DEMO_VILLAGE_CODE))
    ).scalar_one_or_none()
    if not demo:
        return
    has_any = (
        await session.execute(
            select(PrescriptionResultOrm.id).where(PrescriptionResultOrm.village_id == demo.id).limit(1)
        )
    ).scalar_one_or_none()
    if has_any:
        return
    await PrescriptionResultRepository(session)._generate_prescriptions(demo.id)


async def ensure_mvp_qa_credentials(session: AsyncSession) -> None:
    """기존 Neon DB QA 계정 비밀번호를 MVP 제출용(1234)으로 맞춤."""
    import bcrypt

    user = (
        await session.execute(select(UserOrm).where(UserOrm.organization_id == MVP_QA_ORG_UUID))
    ).scalar_one_or_none()
    if not user:
        return
    if bcrypt.checkpw(MVP_QA_PASSWORD.encode(), user.password_hash.encode()):
        return
    user.password_hash = bcrypt.hashpw(MVP_QA_PASSWORD.encode(), bcrypt.gensalt()).decode()
