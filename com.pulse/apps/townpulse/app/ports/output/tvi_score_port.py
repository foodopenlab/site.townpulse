from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.domain.entities.tvi_score_entity import TviScoreEntity


class TviScorePort(ABC):
    @abstractmethod
    async def find_by_id(self, entity_id: UUID) -> TviScoreEntity | None:
        ...

    @abstractmethod
    async def find_latest_by_village(self, village_id: UUID) -> TviScoreEntity | None:
        ...

    @abstractmethod
    async def find_all_latest(
        self, grade_filter: str | None = None, sigun_filter: str | None = None
    ) -> list[TviScoreEntity]:
        ...

    @abstractmethod
    async def find_danger_villages(self, threshold: float = 30.0) -> list[TviScoreEntity]:
        ...

    @abstractmethod
    async def recalculate_all(self) -> int:
        ...
