from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.townpulse.adapter.outbound.orm.models import PublicDataSyncJobOrm
from apps.townpulse.app.dtos.public_data_sync_orchestrator_dto import SyncJobLatestDto
from apps.townpulse.app.ports.output.public_data_sync_orchestrator_port import PublicDataSyncOrchestratorPort


class PublicDataSyncOrchestratorRepository(PublicDataSyncOrchestratorPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_job_started(self, job_type: str) -> UUID:
        job = PublicDataSyncJobOrm(
            id=uuid.uuid4(),
            job_type=job_type,
            status="RUNNING",
            started_at=datetime.utcnow(),
            processed_count=0,
        )
        self._session.add(job)
        await self._session.flush()
        await self._session.commit()
        return job.id

    async def save_job_completed(self, job_id: UUID, processed_count: int) -> None:
        job = await self._session.get(PublicDataSyncJobOrm, job_id)
        if not job:
            return
        job.status = "COMPLETED"
        job.finished_at = datetime.utcnow()
        job.processed_count = processed_count
        await self._session.commit()

    async def save_job_failed(self, job_id: UUID, error_message: str) -> None:
        job = await self._session.get(PublicDataSyncJobOrm, job_id)
        if not job:
            return
        job.status = "FAILED"
        job.finished_at = datetime.utcnow()
        job.error_message = error_message
        await self._session.commit()

    async def get_latest_job(self) -> SyncJobLatestDto | None:
        job = (
            await self._session.execute(
                select(PublicDataSyncJobOrm).order_by(desc(PublicDataSyncJobOrm.started_at)).limit(1)
            )
        ).scalar_one_or_none()
        return self._to_dto(job) if job else None

    async def get_job_by_id(self, job_id: UUID) -> SyncJobLatestDto | None:
        job = await self._session.get(PublicDataSyncJobOrm, job_id)
        return self._to_dto(job) if job else None

    @staticmethod
    def _to_dto(job: PublicDataSyncJobOrm) -> SyncJobLatestDto:
        return SyncJobLatestDto(
            id=str(job.id),
            job_type=job.job_type,
            status=job.status,
            processed_count=job.processed_count,
            started_at=job.started_at.isoformat() if job.started_at else None,
            finished_at=job.finished_at.isoformat() if job.finished_at else None,
            error_message=job.error_message,
        )
