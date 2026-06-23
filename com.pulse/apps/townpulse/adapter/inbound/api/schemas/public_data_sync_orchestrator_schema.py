from __future__ import annotations

from pydantic import BaseModel


class SyncJobResponse(BaseModel):
    job_id: str | None = None
    status: str | None = None
    processed: int | None = None
    tvi_recalculated: int | None = None
    mock: bool | None = None


class SyncJobLatestResponse(BaseModel):
    id: str
    job_type: str
    status: str
    processed_count: int
    started_at: str | None = None
    finished_at: str | None = None
    error_message: str | None = None
