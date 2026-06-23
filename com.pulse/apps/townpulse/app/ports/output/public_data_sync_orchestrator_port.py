from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.public_data_sync_orchestrator_dto import SyncJobLatestDto, SyncTriggerResultDto


class PublicDataSyncOrchestratorPort(ABC):
    @abstractmethod
    async def save_job_started(self, job_type: str) -> UUID:
        ...

    @abstractmethod
    async def save_job_completed(self, job_id: UUID, processed_count: int) -> None:
        ...

    @abstractmethod
    async def save_job_failed(self, job_id: UUID, error_message: str) -> None:
        ...

    @abstractmethod
    async def get_latest_job(self) -> SyncJobLatestDto | None:
        ...

    @abstractmethod
    async def get_job_by_id(self, job_id: UUID) -> SyncJobLatestDto | None:
        ...
