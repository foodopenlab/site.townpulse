"""
내부 QA 관리자 계정(organization 1 + townpulse_user 1)을 DB에 1회 시드.

전제:
  - Alembic 18테이블 마이그레이션 완료
  - town.www/.env.local에 QA_SEED_* 설정 (백엔드 §12-1c · §14)

사용 (백엔드 Oracle session 연결 후):
    cd town.www
    python -m scripts.seed.seed_qa_account

환경변수:
  QA_SEED_ORG_ID      — organization.id (= POST /users/login org_id)
  QA_SEED_PASSWORD    — 평문 비밀번호 (bcrypt 해시 후 password_hash 저장)
  QA_SEED_ORG_NAME    — 선택, 기본 TownPulse QA
  QA_SEED_USER_EMAIL  — 선택, 기본 qa@townpulse.local
  QA_SEED_USER_NAME   — 선택, 기본 QA Admin
"""
from __future__ import annotations

import os
import uuid

import bcrypt


def _require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} 환경변수가 필요합니다 (town.www/.env.local 참고)")
    return value


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, password_hash: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))


async def seed(session) -> dict:
    """organization + admin user 멱등 upsert."""
    org_id = _require_env("QA_SEED_ORG_ID")
    password = _require_env("QA_SEED_PASSWORD")
    org_name = os.environ.get("QA_SEED_ORG_NAME", "TownPulse QA").strip()
    user_email = os.environ.get("QA_SEED_USER_EMAIL", "qa@townpulse.local").strip()
    user_name = os.environ.get("QA_SEED_USER_NAME", "QA Admin").strip()

    try:
        uuid.UUID(org_id)
    except ValueError as exc:
        raise ValueError("QA_SEED_ORG_ID는 UUID 형식이어야 합니다") from exc

    password_hash = hash_password(password)

    await session.execute(
        """
        INSERT INTO organization (id, name, org_type, region_code)
        VALUES (:id, :name, 'qa', '43')
        ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name
        """,
        {"id": org_id, "name": org_name},
    )

    user_id = str(uuid.uuid4())
    await session.execute(
        """
        INSERT INTO townpulse_user (
            id, organization_id, name, email, password_hash, role
        )
        VALUES (:id, :org_id, :name, :email, :password_hash, 'admin')
        ON CONFLICT (email) DO UPDATE SET
            organization_id = EXCLUDED.organization_id,
            name = EXCLUDED.name,
            password_hash = EXCLUDED.password_hash,
            role = 'admin'
        """,
        {
            "id": user_id,
            "org_id": org_id,
            "name": user_name,
            "email": user_email,
            "password_hash": password_hash,
        },
    )

    await session.commit()
    return {
        "organization_id": org_id,
        "user_email": user_email,
        "role": "admin",
    }
