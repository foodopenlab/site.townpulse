from __future__ import annotations

from apps.townpulse.adapter.inbound.api.schemas.public_data_sync_orchestrator_schema import (
    SyncJobLatestResponse,
    SyncJobResponse,
)
from apps.townpulse.app.dtos.public_data_sync_orchestrator_dto import SyncJobLatestDto, SyncTriggerResultDto


class PublicDataSyncOrchestratorMapper:
    @staticmethod
    def to_trigger_response(dto: SyncTriggerResultDto) -> SyncJobResponse:
        return SyncJobResponse(
            job_id=dto.job_id,
            status=dto.status,
            processed=dto.processed,
            tvi_recalculated=dto.tvi_recalculated,
            mock=dto.mock,
        )

    @staticmethod
    def to_latest_job_response(dto: SyncJobLatestDto) -> SyncJobLatestResponse:
        return SyncJobLatestResponse(
            id=dto.id,
            job_type=dto.job_type,
            status=dto.status,
            processed_count=dto.processed_count,
            started_at=dto.started_at,
            finished_at=dto.finished_at,
            error_message=dto.error_message,
        )
