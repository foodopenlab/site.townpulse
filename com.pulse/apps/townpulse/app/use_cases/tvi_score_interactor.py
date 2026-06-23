from __future__ import annotations

from apps.townpulse.app.dtos.tvi_score_dto import (
    TviScoreAllLatestQuery,
    TviScoreAllLatestResult,
    TviScoreDangerQuery,
    TviScoreDangerResult,
    TviScoreLatestItem,
    TviScoreLatestQuery,
    TviScoreLatestResult,
)
from apps.townpulse.app.ports.input.tvi_score_use_case import TviScoreUseCase
from apps.townpulse.app.ports.output.tvi_score_port import TviScorePort
from apps.townpulse.domain.entities.tvi_score_entity import TviScoreEntity


class TviScoreInteractor(TviScoreUseCase):
    def __init__(self, port: TviScorePort) -> None:
        self._port = port

    async def get_latest_by_village(self, query: TviScoreLatestQuery) -> TviScoreLatestResult:
        entity = await self._port.find_latest_by_village(query.village_id)
        if entity is None:
            return TviScoreLatestResult(score=None, found=False)
        return TviScoreLatestResult(score=self._to_item(entity), found=True)

    async def get_all_latest(self, query: TviScoreAllLatestQuery) -> TviScoreAllLatestResult:
        entities = await self._port.find_all_latest(query.grade_filter, query.sigun_filter)
        if query.grade_filter:
            entities = [e for e in entities if e.tvi_grade.grade == query.grade_filter]
        items = [self._to_item(e) for e in entities]
        return TviScoreAllLatestResult(
            scores=items,
            total=len(items),
            danger_count=sum(1 for i in items if i.tvi_grade == "danger"),
            warning_count=sum(1 for i in items if i.tvi_grade == "warning"),
            safe_count=sum(1 for i in items if i.tvi_grade == "safe"),
            avg_tvi_score=round(sum(i.tvi_score for i in items) / len(items), 2) if items else 0.0,
        )

    async def get_danger_villages(self, query: TviScoreDangerQuery) -> TviScoreDangerResult:
        entities = await self._port.find_danger_villages(query.threshold)
        return TviScoreDangerResult(villages=[e.village_id for e in entities], total=len(entities))

    @staticmethod
    def _to_item(entity: TviScoreEntity) -> TviScoreLatestItem:
        grade = entity.tvi_grade
        return TviScoreLatestItem(
            id=entity.id,
            village_id=entity.village_id,
            tvi_score=entity.tvi_score,
            tvi_grade=grade.grade,
            tvi_label=grade.label,
            color_hex=grade.color_hex,
            tvi_delta=entity.tvi_delta,
            risk_level=entity.risk_level,
            calculated_at=entity.calculated_at,
            model_version=entity.model_version,
        )
