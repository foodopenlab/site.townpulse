from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class TviScoreOrm(NeoBase):
    __tablename__ = "tvi_score"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("village.id"), nullable=False)
    calculated_at: Mapped[date] = mapped_column(Date, nullable=False)
    tvi_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(10), nullable=False)
    pop_decline_score: Mapped[float | None] = mapped_column(Float)
    vacancy_rate: Mapped[float | None] = mapped_column(Float)
    bus_interval_score: Mapped[float | None] = mapped_column(Float)
    prev_tvi_score: Mapped[float | None] = mapped_column(Float)
    tvi_delta: Mapped[float | None] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(50), default="weighted_sum_v1")


