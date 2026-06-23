from __future__ import annotations

from uuid import UUID

from apps.townpulse.adapter.inbound.api.schemas.tvi_score_schema import (
    TviScoreAllLatestResponseSchema,
    TviScoreDangerResponseSchema,
    TviScoreLatestItemSchema,
    TviScoreLatestResponseSchema,
)
from apps.townpulse.app.dtos.tvi_score_dto import (
    TviScoreAllLatestQuery,
    TviScoreAllLatestResult,
    TviScoreDangerQuery,
    TviScoreDangerResult,
    TviScoreLatestItem,
    TviScoreLatestQuery,
    TviScoreLatestResult,
)


class TviScoreMapper:
    @staticmethod
    def to_latest_query(village_id: str) -> TviScoreLatestQuery:
        return TviScoreLatestQuery(village_id=UUID(village_id))

    @staticmethod
    def to_all_latest_query(grade: str | None, sigun: str | None) -> TviScoreAllLatestQuery:
        return TviScoreAllLatestQuery(grade_filter=grade, sigun_filter=sigun)

    @staticmethod
    def to_danger_query(threshold: float = 30.0) -> TviScoreDangerQuery:
        return TviScoreDangerQuery(threshold=threshold)

    @staticmethod
    def _to_item_schema(item: TviScoreLatestItem) -> TviScoreLatestItemSchema:
        return TviScoreLatestItemSchema(
            id=str(item.id),
            village_id=str(item.village_id),
            tvi_score=item.tvi_score,
            tvi_grade=item.tvi_grade,
            tvi_label=item.tvi_label,
            color_hex=item.color_hex,
            tvi_delta=item.tvi_delta,
            risk_level=item.risk_level,
            calculated_at=item.calculated_at,
            model_version=item.model_version,
        )

    @staticmethod
    def to_latest_response_schema(result: TviScoreLatestResult) -> TviScoreLatestResponseSchema:
        return TviScoreLatestResponseSchema(
            score=TviScoreMapper._to_item_schema(result.score) if result.score else None,
            found=result.found,
        )

    @staticmethod
    def to_all_latest_response_schema(result: TviScoreAllLatestResult) -> TviScoreAllLatestResponseSchema:
        return TviScoreAllLatestResponseSchema(
            scores=[TviScoreMapper._to_item_schema(s) for s in result.scores],
            total=result.total,
            danger_count=result.danger_count,
            warning_count=result.warning_count,
            safe_count=result.safe_count,
            avg_tvi_score=result.avg_tvi_score,
        )

    @staticmethod
    def to_danger_response_schema(result: TviScoreDangerResult) -> TviScoreDangerResponseSchema:
        return TviScoreDangerResponseSchema(
            villages=[str(v) for v in result.villages],
            total=result.total,
        )
