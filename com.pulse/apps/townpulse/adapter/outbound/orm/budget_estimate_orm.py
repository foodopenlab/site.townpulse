from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class BudgetEstimateOrm(NeoBase):
    __tablename__ = "budget_estimate"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescription_result.id"), nullable=False
    )
    budget_unit_price_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("budget_unit_price.id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    budget_min: Mapped[int] = mapped_column(BigInteger, nullable=False)
    budget_max: Mapped[int] = mapped_column(BigInteger, nullable=False)
    calculation_note: Mapped[str | None] = mapped_column(Text)


