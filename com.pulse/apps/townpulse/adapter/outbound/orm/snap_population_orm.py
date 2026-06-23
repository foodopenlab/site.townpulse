from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class SnapPopulationOrm(NeoBase):
    __tablename__ = "snap_population"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("village.id"), nullable=False)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    population_total: Mapped[int | None] = mapped_column(Integer)
    population_65plus: Mapped[int | None] = mapped_column(Integer)
    population_youth: Mapped[int | None] = mapped_column(Integer)
    registered_households: Mapped[int | None] = mapped_column(Integer)
    net_youth_migration: Mapped[int | None] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


