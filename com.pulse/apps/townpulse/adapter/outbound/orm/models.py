"""Backward-compatible ORM barrel — NeoBase metadata 단일 원천."""
from __future__ import annotations

from apps.townpulse.adapter.outbound.orm.budget_estimate_orm import BudgetEstimateOrm
from apps.townpulse.adapter.outbound.orm.budget_unit_price_orm import BudgetUnitPriceOrm
from apps.townpulse.adapter.outbound.orm.dispatch_rule_orm import DispatchRuleOrm
from apps.townpulse.adapter.outbound.orm.organization_orm import OrganizationOrm
from apps.townpulse.adapter.outbound.orm.prescription_fund_source_orm import PrescriptionFundSourceOrm
from apps.townpulse.adapter.outbound.orm.prescription_indicator_orm import PrescriptionIndicatorOrm
from apps.townpulse.adapter.outbound.orm.prescription_result_orm import PrescriptionResultOrm
from apps.townpulse.adapter.outbound.orm.prescription_type_orm import PrescriptionTypeOrm
from apps.townpulse.adapter.outbound.orm.public_data_sync_orchestrator_orm import PublicDataSyncJobOrm
from apps.townpulse.adapter.outbound.orm.region_orm import RegionOrm
from apps.townpulse.adapter.outbound.orm.report_orm import ReportOrm
from apps.townpulse.adapter.outbound.orm.snap_building_orm import SnapBuildingOrm
from apps.townpulse.adapter.outbound.orm.snap_population_orm import SnapPopulationOrm
from apps.townpulse.adapter.outbound.orm.snap_statistics_orm import SnapStatisticsOrm
from apps.townpulse.adapter.outbound.orm.snap_transport_orm import SnapTransportOrm
from apps.townpulse.adapter.outbound.orm.subscription_orm import SubscriptionOrm
from apps.townpulse.adapter.outbound.orm.tvi_score_orm import TviScoreOrm
from apps.townpulse.adapter.outbound.orm.user_orm import UserOrm
from apps.townpulse.adapter.outbound.orm.village_orm import VillageOrm

__all__ = [
    "RegionOrm",
    "VillageOrm",
    "SnapPopulationOrm",
    "SnapBuildingOrm",
    "SnapTransportOrm",
    "SnapStatisticsOrm",
    "TviScoreOrm",
    "PrescriptionTypeOrm",
    "PrescriptionIndicatorOrm",
    "PrescriptionFundSourceOrm",
    "DispatchRuleOrm",
    "BudgetUnitPriceOrm",
    "PrescriptionResultOrm",
    "BudgetEstimateOrm",
    "OrganizationOrm",
    "SubscriptionOrm",
    "UserOrm",
    "ReportOrm",
    "PublicDataSyncJobOrm",
]
