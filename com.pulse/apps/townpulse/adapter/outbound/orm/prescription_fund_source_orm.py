from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

class PrescriptionFundSourceOrm(NeoBase):
    __tablename__ = "prescription_fund_source"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prescription_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("prescription_type.id"), nullable=False
    )
    fund_name: Mapped[str] = mapped_column(String(200), nullable=False)
    fund_org: Mapped[str | None] = mapped_column(String(100))
    is_eligible: Mapped[bool] = mapped_column(Boolean, default=True)


