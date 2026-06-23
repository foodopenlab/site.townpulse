from __future__ import annotations

from pydantic import BaseModel


class SnapStatisticsResponse(BaseModel):
    id: str
