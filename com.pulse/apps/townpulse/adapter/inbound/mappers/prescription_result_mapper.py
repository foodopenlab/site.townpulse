from __future__ import annotations

from datetime import datetime
from uuid import UUID

from dataclasses import asdict

from apps.townpulse.adapter.inbound.api.schemas.prescription_result_schema import (
    PrescriptionCreateRequest,
    PrescriptionGenerateResponse,
    PrescriptionItemResponse,
    PrescriptionListResponse,
)
from apps.townpulse.app.dtos.prescription_result_dto import (
    PrescriptionItemDto,
    PrescriptionListDto,
    PrescriptionResultGenerateCommand,
    PrescriptionResultGenerateResult,
    PrescriptionResultListResult,
    PrescriptionResultQueryByVillage,
    PrescriptionResultStreamCommand,
)


class PrescriptionResultMapper:
    @staticmethod
    def to_generate_command(body: PrescriptionCreateRequest) -> PrescriptionResultGenerateCommand:
        return PrescriptionResultGenerateCommand(village_id=UUID(body.village_id))

    @staticmethod
    def to_stream_command(prescription_result_id: str) -> PrescriptionResultStreamCommand:
        return PrescriptionResultStreamCommand(prescription_result_id=UUID(prescription_result_id))

    @staticmethod
    def to_query_by_village(village_id: str) -> PrescriptionResultQueryByVillage:
        return PrescriptionResultQueryByVillage(village_id=UUID(village_id))

    @staticmethod
    def to_generate_command_from_village_id(village_id: str) -> PrescriptionResultGenerateCommand:
        return PrescriptionResultGenerateCommand(village_id=UUID(village_id))

    @staticmethod
    def to_list_from_generate(village_id: str, result: PrescriptionResultGenerateResult) -> PrescriptionListResponse:
        return PrescriptionListResponse(
            village_id=village_id,
            prescriptions=[PrescriptionResultMapper.to_item_response(p) for p in result.results],
            generated_at=datetime.utcnow().isoformat(),
        )

    @staticmethod
    def to_item_response(dto: PrescriptionItemDto) -> PrescriptionItemResponse:
        return PrescriptionItemResponse(**asdict(dto))  # type: ignore[arg-type]

    @staticmethod
    def to_generate_response_schema(result: PrescriptionResultGenerateResult) -> PrescriptionGenerateResponse:
        return PrescriptionGenerateResponse(
            prescriptions=[PrescriptionResultMapper.to_item_response(p) for p in result.results],
            total=result.total,
        )

    @staticmethod
    def to_list_response(dto: PrescriptionListDto | PrescriptionResultListResult) -> PrescriptionListResponse:
        return PrescriptionListResponse(
            village_id=dto.village_id,
            prescriptions=[PrescriptionResultMapper.to_item_response(p) for p in dto.prescriptions],
            generated_at=dto.generated_at,
        )
