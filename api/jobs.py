from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from time import perf_counter
from typing import Dict, Literal, Optional
from uuid import uuid4

from receipt_reader.types import Invoice

JobStatus = Literal["queued", "processing", "completed", "failed"]


@dataclass
class Job:
    id: str = field(default_factory=lambda: str(uuid4()))
    status: JobStatus = "queued"
    result: Optional[Invoice] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None
    duration_seconds: Optional[float] = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = Lock()

    def create(self, *, metadata: Optional[dict] = None) -> Job:
        job = Job(metadata=metadata)
        with self._lock:
            self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)

    def mark_processing(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "processing"
            return job

    def mark_completed(self, job_id: str, *, invoice: Invoice, duration: float) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "completed"
            job.result = invoice
            job.duration_seconds = duration
            return job

    def mark_failed(self, job_id: str, *, error: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.status = "failed"
            job.error = error
            return job

    def reset(self) -> None:
        with self._lock:
            self._jobs.clear()


def timed(fn, *args, **kwargs):
    start = perf_counter()
    value = fn(*args, **kwargs)
    duration = perf_counter() - start
    return value, duration