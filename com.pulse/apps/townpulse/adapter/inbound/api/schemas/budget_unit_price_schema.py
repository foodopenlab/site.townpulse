from __future__ import annotations

from pydantic import BaseModel


class BudgetUnitPriceResponse(BaseModel):
    id: str
