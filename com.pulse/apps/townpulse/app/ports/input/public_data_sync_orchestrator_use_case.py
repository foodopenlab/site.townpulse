from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from apps.townpulse.app.dtos.public_data_sync_orchestrator_dto import SyncJobLatestDto, SyncTriggerResultDto


class PublicDataSyncOrchestratorUseCase(ABC):
    @abstractmethod
    async def collect_core(self, *, limit: int | None = None) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def collect_all_core(
        self,
        *,
        offset: int | None = None,
        limit: int | None = None,
        sync_dong_code: bool = True,
        sync_core: bool = True,
        sync_transport: bool = True,
        sigungu_code: str | None = None,
        sync_tvi: bool = True,
    ) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def collect_migration_chunk(self, chunk_index: int) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def finalize_monthly_snap(self) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def collect_all(self) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def ingest_fiscal_all(self) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def trigger_sync(self) -> SyncTriggerResultDto:
        ...

    @abstractmethod
    async def get_latest_job(self) -> SyncJobLatestDto | None:
        ...

    @abstractmethod
    async def get_job_by_id(self, job_id: UUID) -> SyncJobLatestDto | None:
        ...
