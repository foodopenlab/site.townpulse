from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

if TYPE_CHECKING:
    from apps.townpulse.adapter.outbound.orm.village_orm import VillageOrm

class RegionOrm(NeoBase):
    __tablename__ = "region"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sido: Mapped[str] = mapped_column(String(20), nullable=False)
    sigungu: Mapped[str] = mapped_column(String(50), nullable=False)
    sigungu_code: Mapped[str | None] = mapped_column(String(5))
    emd_name: Mapped[str] = mapped_column(String(100), nullable=False)
    emd_code: Mapped[str | None] = mapped_column(String(10), unique=True)
    legal_dong_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    tago_city_code: Mapped[str | None] = mapped_column(String(10))
    area_km2: Mapped[float | None] = mapped_column(Float)
    fiscal_self_reliance: Mapped[float | None] = mapped_column(Float)
    fiscal_data_year: Mapped[date | None] = mapped_column(Date)
    birth_rate: Mapped[float | None] = mapped_column(Float)
    daytime_population: Mapped[float | None] = mapped_column(Float)
    demographic_data_year: Mapped[date | None] = mapped_column(Date)

    villages: Mapped[list["VillageOrm"]] = relationship(back_populates="region")


