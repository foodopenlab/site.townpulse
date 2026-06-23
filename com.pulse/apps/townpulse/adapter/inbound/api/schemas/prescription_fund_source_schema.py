from __future__ import annotations

from pydantic import BaseModel


class PrescriptionFundSourceResponse(BaseModel):
    id: str
