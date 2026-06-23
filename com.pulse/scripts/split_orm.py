"""Split monolithic models.py into per-domain ORM modules."""
from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "apps" / "townpulse" / "adapter" / "outbound" / "orm" / "models.py"
ORM_DIR = SRC.parent

# class name -> file stem (without _orm)
MAPPING = {
    "RegionOrm": "region",
    "VillageOrm": "village",
    "SnapPopulationOrm": "snap_population",
    "SnapBuildingOrm": "snap_building",
    "SnapTransportOrm": "snap_transport",
    "SnapStatisticsOrm": "snap_statistics",
    "TviScoreOrm": "tvi_score",
    "PrescriptionTypeOrm": "prescription_type",
    "PrescriptionIndicatorOrm": "prescription_indicator",
    "PrescriptionFundSourceOrm": "prescription_fund_source",
    "DispatchRuleOrm": "dispatch_rule",
    "BudgetUnitPriceOrm": "budget_unit_price",
    "PrescriptionResultOrm": "prescription_result",
    "BudgetEstimateOrm": "budget_estimate",
    "OrganizationOrm": "organization",
    "SubscriptionOrm": "subscription",
    "UserOrm": "user",
    "ReportOrm": "report",
    "PublicDataSyncJobOrm": "public_data_sync_orchestrator",
}

HEADER = '''from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.matrix.grid_neo_theone_base import NeoBase

'''

if __name__ == "__main__":
    text = SRC.read_text(encoding="utf-8")
    lines = text.splitlines()
    classes: dict[str, list[str]] = {}
    current = None
    for line in lines:
        if line.startswith("class ") and line.endswith("(NeoBase):"):
            current = line.split()[1].split("(")[0]
            classes[current] = [line]
        elif current:
            classes[current].append(line)
            if line and not line[0].isspace() and not line.startswith("class "):
                current = None

    for cls, body in classes.items():
        stem = MAPPING.get(cls, cls.replace("Orm", "").lower())
        path = ORM_DIR / f"{stem}_orm.py"
        content = HEADER + "\n".join(body) + "\n"
        path.write_text(content, encoding="utf-8")
        print("wrote", path.name)
