from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class SnapStatisticsOrm(NeoBase):
    __tablename__ = "snap_statistics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("village.id"), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    aging_ratio: Mapped[float | None] = mapped_column(Float)
    youth_ratio: Mapped[float | None] = mapped_column(Float)
    pop_density: Mapped[float | None] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


