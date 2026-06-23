from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from apps.townpulse.adapter.inbound.api.schemas.tvi_score_schema import (
    TviScoreAllLatestResponseSchema,
    TviScoreDangerResponseSchema,
    TviScoreLatestResponseSchema,
)
from apps.townpulse.adapter.inbound.mappers.tvi_score_mapper import TviScoreMapper
from apps.townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from apps.townpulse.dependencies.tvi_score_provider import get_tvi_score_use_case
from core.matrix.grid_trinity_hacker_mixin import CurrentUser

tvi_score_router = APIRouter(prefix="/tvi-scores", tags=["tvi_score"])


@tvi_score_router.get("", response_model=TviScoreAllLatestResponseSchema)
async def get_all_latest(
    _user: CurrentUser,
    grade: str | None = Query(None),
    sigun: str | None = Query(None),
    use_case: TviScoreUseCase = Depends(get_tvi_score_use_case),
):
    query = TviScoreMapper.to_all_latest_query(grade, sigun)
    result = await use_case.get_all_latest(query)
    return TviScoreMapper.to_all_latest_response_schema(result)


@tvi_score_router.get("/danger", response_model=TviScoreDangerResponseSchema)
async def get_danger_villages(
    _user: CurrentUser,
    threshold: float = Query(30.0),
    use_case: TviScoreUseCase = Depends(get_tvi_score_use_case),
):
    query = TviScoreMapper.to_danger_query(threshold)
    result = await use_case.get_danger_villages(query)
    return TviScoreMapper.to_danger_response_schema(result)


@tvi_score_router.get("/{village_id}/latest", response_model=TviScoreLatestResponseSchema)
async def get_latest_by_village(
    village_id: str,
    _user: CurrentUser,
    use_case: TviScoreUseCase = Depends(get_tvi_score_use_case),
):
    query = TviScoreMapper.to_latest_query(village_id)
    result = await use_case.get_latest_by_village(query)
    return TviScoreMapper.to_latest_response_schema(result)
