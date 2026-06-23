from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class PrescriptionIndicatorOrm(NeoBase):
    __tablename__ = "prescription_indicator"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescription_type.id"), nullable=False
    )
    indicator_code: Mapped[str] = mapped_column(String(50), nullable=False)
    effect_direction: Mapped[str] = mapped_column(String(20), nullable=False)


