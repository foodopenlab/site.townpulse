from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class BudgetUnitPriceOrm(NeoBase):
    __tablename__ = "budget_unit_price"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescription_type.id"), nullable=False
    )
    unit: Mapped[str] = mapped_column(String(20), nullable=False)
    price_min: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_max: Mapped[int] = mapped_column(BigInteger, nullable=False)
    reference_source: Mapped[str | None] = mapped_column(String(300))
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)


