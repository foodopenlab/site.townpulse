from __future__ import annotations

from apps.townpulse.adapter.outbound.orm.tvi_score_orm import TviScoreOrm
from apps.townpulse.domain.entities.tvi_score_entity import TviScoreEntity


class TviScoreOrmMapper:
    @staticmethod
    def to_entity(orm_obj: TviScoreOrm) -> TviScoreEntity:
        return TviScoreEntity(
            id=orm_obj.id,
            village_id=orm_obj.village_id,
            calculated_at=orm_obj.calculated_at,
            tvi_score=orm_obj.tvi_score,
            risk_level=orm_obj.risk_level,
            pop_decline_score=orm_obj.pop_decline_score,
            vacancy_rate=orm_obj.vacancy_rate,
            bus_interval_score=orm_obj.bus_interval_score,
            prev_tvi_score=orm_obj.prev_tvi_score,
            tvi_delta=orm_obj.tvi_delta,
            model_version=orm_obj.model_version,
        )
