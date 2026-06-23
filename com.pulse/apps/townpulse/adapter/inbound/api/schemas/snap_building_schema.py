from __future__ import annotations

from pydantic import BaseModel


class SnapBuildingResponse(BaseModel):
    id: str
