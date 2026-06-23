from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator

from apps.townpulse.app.dtos.prescription_result_dto import (
    PrescriptionResultGenerateCommand,
    PrescriptionResultGenerateResult,
    PrescriptionResultListResult,
    PrescriptionResultQueryByVillage,
    PrescriptionResultStreamCommand,
)


class PrescriptionResultUseCase(ABC):
    @abstractmethod
    async def generate_for_village(
        self, command: PrescriptionResultGenerateCommand
    ) -> PrescriptionResultGenerateResult:
        ...

    @abstractmethod
    async def find_by_village(self, query: PrescriptionResultQueryByVillage) -> PrescriptionResultListResult:
        ...

    @abstractmethod
    async def stream_ai_description(self, command: PrescriptionResultStreamCommand) -> AsyncGenerator[str, None]:
        raise NotImplementedError
        yield ""
