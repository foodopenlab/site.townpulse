from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from apps.townpulse.adapter.inbound.api.schemas.prescription_result_schema import (
    PrescriptionCreateRequest,
    PrescriptionGenerateResponse,
    PrescriptionListResponse,
)
from apps.townpulse.adapter.inbound.mappers.prescription_result_mapper import PrescriptionResultMapper
from apps.townpulse.app.ports.input.prescription_result_use_case import PrescriptionResultUseCase
from apps.townpulse.dependencies.prescription_result_provider import get_prescription_result_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser, WriteUser, verify_sse_token

prescription_result_router = APIRouter(prefix="/prescription-results", tags=["prescription_result"])


@prescription_result_router.post("", response_model=PrescriptionGenerateResponse)
async def create_prescription(
    body: PrescriptionCreateRequest,
    _user: WriteUser,
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
):
    try:
        command = PrescriptionResultMapper.to_generate_command(body)
        result = await use_case.generate_for_village(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PrescriptionResultMapper.to_generate_response_schema(result)


@prescription_result_router.get("/by-village/{village_id}", response_model=PrescriptionListResponse)
async def list_prescriptions(
    village_id: str,
    _user: CurrentUser,
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
):
    query = PrescriptionResultMapper.to_query_by_village(village_id)
    result = await use_case.find_by_village(query)
    if not result.prescriptions:
        try:
            command = PrescriptionResultMapper.to_generate_command_from_village_id(village_id)
            generated = await use_case.generate_for_village(command)
            if generated.results:
                return PrescriptionResultMapper.to_list_from_generate(village_id, generated)
        except ValueError:
            pass
    return PrescriptionResultMapper.to_list_response(result)


@prescription_result_router.get("/{prescription_id}/stream")
async def stream_prescription(
    prescription_id: str,
    _user: dict = Depends(verify_sse_token),
    use_case: PrescriptionResultUseCase = Depends(get_prescription_result_use_case),
):
    command = PrescriptionResultMapper.to_stream_command(prescription_id)

    async def event_stream():
        stream: AsyncGenerator[str, None] = use_case.stream_ai_description(command)
        try:
            async for chunk in stream:
                yield f"data: {chunk}\n\n"
        except ValueError as exc:
            yield f"data: ERROR: {exc}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
