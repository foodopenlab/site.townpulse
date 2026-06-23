from __future__ import annotations

from pydantic import BaseModel


class PrescriptionIndicatorResponse(BaseModel):
    id: str
