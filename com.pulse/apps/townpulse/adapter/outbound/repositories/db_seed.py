from __future__ import annotations

import os
import uuid
from datetime import date, datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import (
    BudgetEstimateOrm,
    BudgetUnitPriceOrm,
    DispatchRuleOrm,
    OrganizationOrm,
    PrescriptionFundSourceOrm,
    PrescriptionIndicatorOrm,
    PrescriptionResultOrm,
    PrescriptionTypeOrm,
    PublicDataSyncJobOrm,
    RegionOrm,
    ReportOrm,
    SnapBuildingOrm,
    SnapPopulationOrm,
    SnapStatisticsOrm,
    SnapTransportOrm,
    SubscriptionOrm,
    TviScoreOrm,
    UserOrm,
    VillageOrm,
)
from apps.townpulse.services.seed_data import (
    BUDGET_PRICES,
    DEMO_VILLAGE_CODE,
    DISPATCH_RULES,
    MVP_QA_ORG_UUID,
    MVP_QA_PASSWORD,
    PRESCRIPTION_TYPES,
    PRESCRIPTION_INDICATORS,
    SIGUNGU_SEED,
    generate_village_rows,
)
from apps.townpulse.services.tvi_calculator import (
    calculate_bus_interval_score,
    calculate_pop_decline_raw,
    calculate_tvi,
    calculate_vacancy_score,
    grade_from_score,
    normalize_min_max,
)
import bcrypt


async def _seed_mock_snaps_and_tvi(session: AsyncSession, villages: list[VillageOrm]) -> None:
    """SEED_MOCK_SNAPS=1 일 때만 합성 SNAP/TVI 생성."""
    snapshot_date = date(2025, 5, 1)
    raw_scores: list[float] = []
    village_metrics: list[dict] = []

    for idx, village in enumerate(villages):
        is_demo = village.emd_code == DEMO_VILLAGE_CODE
        is_jeungpyeong = village.emd_code and village.emd_code.startswith("43745")
        pop_total = 800 if is_demo else 1200 + (idx % 40) * 50
        pop_65 = int(pop_total * (0.35 if is_demo else 0.2 + (idx % 10) * 0.02))
        pop_youth = int(pop_total * (0.08 if is_demo else 0.12))
        households = max(100, pop_total // 2)
        net_mig = -15 if is_demo else -5 - (idx % 7)
        residential = 120 if is_demo else 80 + idx % 30
        bus_routes = None if is_jeungpyeong else (0 if is_demo else 2 + idx % 5)
        avg_interval = 75.0 if is_demo else 25.0 + (idx % 8) * 5
        nearest_stop = 2500 if is_demo else 300 + (idx % 10) * 100
        stops_1km = 0 if is_demo else 1 + idx % 4
        elderly_rate = pop_65 / pop_total
        youth_ratio = pop_youth / pop_total
        vacancy_rate = 0.22 if is_demo else 0.05 + (idx % 15) * 0.01
        pop_change = -0.08 if is_demo else -0.01 - (idx % 5) * 0.005

        session.add(
            SnapPopulationOrm(
                id=uuid.uuid4(),
                village_id=village.id,
                snapshot_date=snapshot_date,
                population_total=pop_total,
                population_65plus=pop_65,
                population_youth=pop_youth,
                registered_households=households,
                net_youth_migration=net_mig,
            )
        )
        session.add(
            SnapBuildingOrm(
                id=uuid.uuid4(),
                village_id=village.id,
                snapshot_date=snapshot_date,
                residential_buildings=residential,
            )
        )
        session.add(
            SnapTransportOrm(
                id=uuid.uuid4(),
                village_id=village.id,
                snapshot_date=snapshot_date,
                bus_route_count=bus_routes,
                avg_bus_interval_min=avg_interval,
                nearest_stop_distance_m=nearest_stop,
                bus_stops_within_1km=stops_1km,
            )
        )
        session.add(
            SnapStatisticsOrm(
                id=uuid.uuid4(),
                village_id=village.id,
                snapshot_date=snapshot_date,
                aging_ratio=elderly_rate,
                youth_ratio=youth_ratio,
                pop_density=pop_total / 10.0,
            )
        )

        raw = calculate_pop_decline_raw(pop_change, elderly_rate, youth_ratio, net_mig, households)
        raw_scores.append(raw)
        bus_score = calculate_bus_interval_score(bus_routes or 0, avg_interval, nearest_stop, stops_1km)
        village_metrics.append(
            {
                "village": village,
                "raw": raw,
                "vacancy_rate": vacancy_rate,
                "bus_score": bus_score,
            }
        )

    vmin, vmax = min(raw_scores), max(raw_scores)
    for m in village_metrics:
        pop_norm = normalize_min_max(m["raw"], vmin, vmax)
        vac_score = calculate_vacancy_score(m["vacancy_rate"])
        tvi = calculate_tvi(pop_norm, vac_score, m["bus_score"])
        if m["village"].emd_code == DEMO_VILLAGE_CODE:
            tvi = 12.0
        session.add(
            TviScoreOrm(
                id=uuid.uuid4(),
                village_id=m["village"].id,
                calculated_at=snapshot_date,
                tvi_score=tvi,
                risk_level=grade_from_score(tvi),
                pop_decline_score=pop_norm,
                vacancy_rate=m["vacancy_rate"],
                bus_interval_score=m["bus_score"],
            )
        )


async def seed_database(session: AsyncSession) -> dict:
    for model in (
        BudgetEstimateOrm,
        ReportOrm,
        PrescriptionResultOrm,
        TviScoreOrm,
        SnapStatisticsOrm,
        SnapTransportOrm,
        SnapBuildingOrm,
        SnapPopulationOrm,
        VillageOrm,
        DispatchRuleOrm,
        BudgetUnitPriceOrm,
        PrescriptionFundSourceOrm,
        PrescriptionIndicatorOrm,
        PrescriptionTypeOrm,
        SubscriptionOrm,
        UserOrm,
        OrganizationOrm,
        PublicDataSyncJobOrm,
        RegionOrm,
    ):
        await session.execute(delete(model))

    region_map: dict[str, RegionOrm] = {}
    for sig in SIGUNGU_SEED:
        region = RegionOrm(
            id=uuid.uuid4(),
            sido="충청북도",
            sigungu=sig["sigungu"],
            sigungu_code=sig["sigungu_code"],
            emd_name=sig["sigungu"],
            emd_code=None,
            legal_dong_code=f"{sig['sigungu_code']}00000",
            tago_city_code=sig["tago_city_code"],
            fiscal_self_reliance=45.0 + int(sig["sigungu_code"][-1]),
            fiscal_data_year=date(2024, 1, 1),
        )
        session.add(region)
        region_map[sig["sigungu"]] = region

    prescription_types: dict[str, PrescriptionTypeOrm] = {}
    for pt in PRESCRIPTION_TYPES:
        orm = PrescriptionTypeOrm(
            id=uuid.uuid4(),
            code=pt["code"],
            name=pt["name"],
            category=pt["category"],
            rollout_timeline=pt["rollout_timeline"],
            is_active=True,
        )
        session.add(orm)
        prescription_types[pt["code"]] = orm

    await session.flush()

    for pt in PRESCRIPTION_TYPES:
        orm = prescription_types[pt["code"]]
        session.add(
            PrescriptionFundSourceOrm(
                id=uuid.uuid4(),
                prescription_type_id=orm.id,
                fund_name=f"{pt['name']} 지원기금",
                fund_org="충북도",
                is_eligible=True,
            )
        )

    await session.flush()

    for dr in DISPATCH_RULES:
        session.add(
            DispatchRuleOrm(
                id=uuid.uuid4(),
                prescription_type_id=prescription_types[dr["code"]].id,
                trigger_indicator=dr["trigger"],
                operator=dr["operator"],
                threshold_value=dr["threshold"],
                priority_rank=dr["rank"],
            )
        )

    for bp in BUDGET_PRICES:
        session.add(
            BudgetUnitPriceOrm(
                id=uuid.uuid4(),
                prescription_type_id=prescription_types[bp["code"]].id,
                unit=bp["unit"],
                price_min=bp["min"],
                price_max=bp["max"],
                reference_source="MVP 시드",
                effective_from=date(2025, 1, 1),
            )
        )

    for pi in PRESCRIPTION_INDICATORS:
        session.add(
            PrescriptionIndicatorOrm(
                id=uuid.uuid4(),
                prescription_type_id=prescription_types[pi["code"]].id,
                indicator_code=pi["indicator_code"],
                effect_direction=pi["effect_direction"],
            )
        )

    villages: list[VillageOrm] = []
    for row in generate_village_rows(228):
        region = region_map[row["sigungu"]]
        village = VillageOrm(
            id=uuid.uuid4(),
            region_id=region.id,
            name=row["name"],
            emd_code=row["emd_code"],
            lat=row["lat"],
            lng=row["lng"],
            last_synced_at=datetime.utcnow(),
        )
        session.add(village)
        villages.append(village)

    await session.flush()

    seed_mock = os.getenv("SEED_MOCK_SNAPS", "0").lower() in ("1", "true", "yes")
    if seed_mock:
        await _seed_mock_snaps_and_tvi(session, villages)

    org_id = MVP_QA_ORG_UUID
    org = OrganizationOrm(id=org_id, name="TownPulse QA", org_type="local_gov", region_code="43")
    session.add(org)
    pwd_hash = bcrypt.hashpw(MVP_QA_PASSWORD.encode(), bcrypt.gensalt()).decode()
    session.add(
        UserOrm(
            id=uuid.uuid4(),
            organization_id=org_id,
            name="QA Admin",
            email="qa@townpulse.local",
            password_hash=pwd_hash,
            role="admin",
        )
    )
    session.add(
        SubscriptionOrm(
            id=uuid.uuid4(),
            organization_id=org_id,
            tier="trial",
            started_at=date(2025, 1, 1),
            expires_at=date(2026, 12, 31),
            is_active=True,
            monthly_fee=0,
        )
    )

    await session.flush()
    count = await session.scalar(select(func.count()).select_from(VillageOrm))

    demo_village = (
        await session.execute(select(VillageOrm).where(VillageOrm.emd_code == DEMO_VILLAGE_CODE))
    ).scalar_one_or_none()
    if demo_village:
        from apps.townpulse.adapter.outbound.repositories.prescription_result_repository import PrescriptionResultRepository

        await PrescriptionResultRepository(session)._generate_prescriptions(demo_village.id)

    return {"villages": count, "demo_village": DEMO_VILLAGE_CODE}
