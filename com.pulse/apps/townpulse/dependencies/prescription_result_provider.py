from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository
from apps.townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from apps.townpulse.app.ports.output.budget_estimate_port import BudgetEstimatePort
from apps.townpulse.app.ports.output.dispatch_rule_port import DispatchRulePort
from apps.townpulse.app.ports.output.prescription_fund_source_port import PrescriptionFundSourcePort
from apps.townpulse.app.ports.output.prescription_result_port import PrescriptionResultPort
from apps.townpulse.app.ports.output.prescription_type_port import PrescriptionTypePort
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.app.ports.output.village_port import VillagePort
from apps.townpulse.app.use_cases.prescription_result_interactor import PrescriptionResultInteractor
from apps.townpulse.dependencies.budget_estimate_provider import get_budget_estimate_repository
from apps.townpulse.dependencies.dispatch_rule_provider import get_dispatch_rule_repository
from apps.townpulse.dependencies.prescription_fund_source_provider import get_prescription_fund_source_repository
from apps.townpulse.dependencies.prescription_type_provider import get_prescription_type_repository
from apps.townpulse.dependencies.tvi_score_provider import get_tvi_score_repository
from apps.townpulse.dependencies.village_provider import get_village_repository
from core.matrix.grid_oracle_database_manager import get_db


def get_prescription_result_repository(session: AsyncSession = Depends(get_db)) -> PrescriptionResultPort:
    return PrescriptionResultRepository(session)


def get_prescription_result_use_case(
    result_repo: PrescriptionResultPort = Depends(get_prescription_result_repository),
    dispatch_repo: DispatchRulePort = Depends(get_dispatch_rule_repository),
    village_repo: VillagePort = Depends(get_village_repository),
    tvi_score_repo: TviScorePort = Depends(get_tvi_score_repository),
    prescription_type_repo: PrescriptionTypePort = Depends(get_prescription_type_repository),
    fund_source_repo: PrescriptionFundSourcePort = Depends(get_prescription_fund_source_repository),
    budget_estimate_repo: BudgetEstimatePort = Depends(get_budget_estimate_repository),
) -> PrescriptionResultUseCase:
    return PrescriptionResultInteractor(
        result_repo,
        dispatch_repo,
        village_repo,
        tvi_score_repo,
        prescription_type_repo,
        fund_source_repo,
        budget_estimate_repo,
    )
