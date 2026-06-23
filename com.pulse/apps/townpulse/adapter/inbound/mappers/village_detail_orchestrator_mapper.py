from __future__ import annotations

from dataclasses import asdict

from apps.townpulse.adapter.inbound.api.schemas.prescription_result_schema import PrescriptionItemResponse
from apps.townpulse.adapter.inbound.api.schemas.village_detail_orchestrator_schema import (
    SnapTransportResponse,
    VillageDetailResponse,
)
from apps.townpulse.app.dtos.village_detail_orchestrator_dto import VillageDetailDto


class VillageDetailOrchestratorMapper:
    @staticmethod
    def to_response(dto: VillageDetailDto) -> VillageDetailResponse:
        snap = None
        if dto.snap_transport:
            snap = SnapTransportResponse(**asdict(dto.snap_transport))
        return VillageDetailResponse(
            village_id=dto.village_id,
            village_code=dto.village_code,
            village_name=dto.village_name,
            sigun_name=dto.sigun_name,
            tvi_score=dto.tvi_score,
            tvi_grade=dto.tvi_grade,  # type: ignore[arg-type]
            bus_interval_score=dto.bus_interval_score,
            vacant_house_rate=dto.vacant_house_rate,
            elderly_rate=dto.elderly_rate,
            bus_interval_minutes=dto.bus_interval_minutes,
            nearest_stop_distance_m=dto.nearest_stop_distance_m,
            bus_stops_within_1km=dto.bus_stops_within_1km,
            transport_gap=dto.transport_gap,
            population_change_rate=dto.population_change_rate,
            extinction_probability_5y=dto.extinction_probability_5y,
            snap_transport=snap,
            updated_at=dto.updated_at,
            prescriptions_preview=[
                PrescriptionItemResponse(**asdict(p))  # type: ignore[arg-type]
                for p in dto.prescriptions_preview
            ],
        )
