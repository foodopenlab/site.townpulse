"""townpulse_router — MVP 활성 router 집계 (v9.5 §4-2)."""
from __future__ import annotations

from fastapi import APIRouter

from apps.townpulse.adapter.inbound.api.v1.budget_estimate_router import budget_estimate_router
from apps.townpulse.adapter.inbound.api.v1.budget_unit_price_router import budget_unit_price_router
from apps.townpulse.adapter.inbound.api.v1.dashboard_orchestrator_router import dashboard_orchestrator_router
from apps.townpulse.adapter.inbound.api.v1.dispatch_rule_router import dispatch_rule_router
from apps.townpulse.adapter.inbound.api.v1.organization_router import organization_router
from apps.townpulse.adapter.inbound.api.v1.prescription_fund_source_router import prescription_fund_source_router
from apps.townpulse.adapter.inbound.api.v1.prescription_indicator_router import prescription_indicator_router
from apps.townpulse.adapter.inbound.api.v1.prescription_result_router import prescription_result_router
from apps.townpulse.adapter.inbound.api.v1.prescription_type_router import prescription_type_router
from apps.townpulse.adapter.inbound.api.v1.public_data_sync_orchestrator_router import public_data_sync_orchestrator_router
from apps.townpulse.adapter.inbound.api.v1.region_router import region_router
from apps.townpulse.adapter.inbound.api.v1.report_orchestrator_router import report_orchestrator_router
from apps.townpulse.adapter.inbound.api.v1.report_router import report_router
from apps.townpulse.adapter.inbound.api.v1.snap_building_router import snap_building_router
from apps.townpulse.adapter.inbound.api.v1.snap_population_router import snap_population_router
from apps.townpulse.adapter.inbound.api.v1.snap_statistics_router import snap_statistics_router
from apps.townpulse.adapter.inbound.api.v1.snap_transport_router import snap_transport_router
from apps.townpulse.adapter.inbound.api.v1.subscription_router import subscription_router
from apps.townpulse.adapter.inbound.api.v1.tvi_score_router import tvi_score_router
from apps.townpulse.adapter.inbound.api.v1.user_router import user_router
from apps.townpulse.adapter.inbound.api.v1.village_detail_orchestrator_router import village_detail_orchestrator_router
from apps.townpulse.adapter.inbound.api.v1.village_router import village_router

townpulse_router = APIRouter(prefix="/townpulse")

ROUTERS = [
    region_router,
    village_router,
    snap_population_router,
    snap_building_router,
    snap_transport_router,
    snap_statistics_router,
    tvi_score_router,
    prescription_type_router,
    prescription_indicator_router,
    prescription_fund_source_router,
    dispatch_rule_router,
    budget_unit_price_router,
    prescription_result_router,
    budget_estimate_router,
    organization_router,
    subscription_router,
    user_router,
    report_router,
    dashboard_orchestrator_router,
    village_detail_orchestrator_router,
    report_orchestrator_router,
    public_data_sync_orchestrator_router,
]

for router in ROUTERS:
    townpulse_router.include_router(router)
