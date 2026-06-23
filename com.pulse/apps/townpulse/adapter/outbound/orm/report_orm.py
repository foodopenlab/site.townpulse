from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class ReportOrm(NeoBase):
    __tablename__ = "report"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("townpulse_user.id"), nullable=False)
    village_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("village.id"), nullable=False)
    tvi_score_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tvi_score.id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String(300))
    format: Mapped[str] = mapped_column(String(20), default="pdf")
    file_url: Mapped[str | None] = mapped_column(String(1000))
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


