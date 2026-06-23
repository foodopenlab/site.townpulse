from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from uuid import UUID

from apps.townpulse.app.dtos.prescription_result_dto import PrescriptionItemDto, PrescriptionListDto


class PrescriptionResultPort(ABC):
    @abstractmethod
    async def generate_for_village(self, village_id: UUID) -> list[PrescriptionItemDto]:
        ...

    @abstractmethod
    async def find_by_village(self, village_id: UUID) -> PrescriptionListDto:
        ...

    @abstractmethod
    async def stream_ai_description(self, prescription_id: UUID) -> AsyncGenerator[str, None]:
        raise NotImplementedError
        yield ""
