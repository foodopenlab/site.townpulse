from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class PrescriptionResultOrm(NeoBase):
    __tablename__ = "prescription_result"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("village.id"), nullable=False)
    tvi_score_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tvi_score.id"), nullable=False)
    prescription_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescription_type.id"), nullable=False
    )
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False)
    tvi_gain_min: Mapped[float | None] = mapped_column(Float)
    tvi_gain_max: Mapped[float | None] = mapped_column(Float)
    fund_applicable: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_description: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


