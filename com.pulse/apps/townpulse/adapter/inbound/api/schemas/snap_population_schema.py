from __future__ import annotations

from pydantic import BaseModel


class SnapPopulationResponse(BaseModel):
    id: str
