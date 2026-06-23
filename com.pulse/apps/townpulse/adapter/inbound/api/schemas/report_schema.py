from __future__ import annotations

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: str
