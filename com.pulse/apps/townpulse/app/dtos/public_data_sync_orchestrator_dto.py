from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyncTriggerResultDto:
    job_id: str
    status: str
    processed: int
    tvi_recalculated: int
    mock: bool


@dataclass(slots=True)
class SyncJobLatestDto:
    id: str
    job_type: str
    status: str
    processed_count: int
    started_at: str | None
    finished_at: str | None
    error_message: str | None = None
