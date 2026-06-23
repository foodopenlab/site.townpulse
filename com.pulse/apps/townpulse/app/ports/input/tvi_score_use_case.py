from __future__ import annotations

from abc import ABC, abstractmethod

from apps.townpulse.app.dtos.tvi_score_dto import (
    TviScoreAllLatestQuery,
    TviScoreAllLatestResult,
    TviScoreDangerQuery,
    TviScoreDangerResult,
    TviScoreLatestQuery,
    TviScoreLatestResult,
)


class TviScoreUseCase(ABC):
    @abstractmethod
    async def get_latest_by_village(self, query: TviScoreLatestQuery) -> TviScoreLatestResult:
        ...

    @abstractmethod
    async def get_all_latest(self, query: TviScoreAllLatestQuery) -> TviScoreAllLatestResult:
        ...

    @abstractmethod
    async def get_danger_villages(self, query: TviScoreDangerQuery) -> TviScoreDangerResult:
        ...
