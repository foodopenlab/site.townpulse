"""create_townpulse_18_tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-22

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from apps.townpulse.adapter.outbound.orm import models  # noqa: F401
    from core.matrix.grid_neo_theone_base import NeoBase

    bind = op.get_bind()
    NeoBase.metadata.create_all(bind)


def downgrade() -> None:
    from apps.townpulse.adapter.outbound.orm import models  # noqa: F401
    from core.matrix.grid_neo_theone_base import NeoBase

    bind = op.get_bind()
    NeoBase.metadata.drop_all(bind)
