from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

if TYPE_CHECKING:
    from apps.townpulse.adapter.outbound.orm.region_orm import RegionOrm

class VillageOrm(NeoBase):
    __tablename__ = "village"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("region.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    emd_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    lat: Mapped[float | None] = mapped_column(Float)
    lng: Mapped[float | None] = mapped_column(Float)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime)

    region: Mapped["RegionOrm"] = relationship(back_populates="villages")


