from __future__ import annotations
from typing import Dict, Literal, Optional
from pydantic import BaseModel, Field
import uuid

from receipt_reader import parser
from receipt_reader.types import Invoice

JobId = str
JobStatus = Literal["pending", "processing", "completed", "failed"]


class Job(BaseModel):
    id: JobId = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = "pending"
    result: Optional[Invoice] = None
    error_message: Optional[str] = None


_jobs: Dict[JobId, Job] = {}


class JobStore:
    def __init__(self, jobs: Dict[JobId, Job]):
        self._jobs = jobs

    def create(self) -> Job:
        job = Job()
        self._jobs[job.id] = job
        return job

    def get(self, job_id: JobId) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job_id: JobId, status: JobStatus, result: Optional[Invoice] = None, error_message: Optional[str] = None):
        if job := self._jobs.get(job_id):
            job.status = status
            job.result = result
            job.error_message = error_message


def get_store() -> JobStore:
    return JobStore(_jobs)


async def process_job(job_id: JobId, file_path: str):
    """
    Processes a parsing job in the background.
    """
    store = get_store()
    store.update(job_id, "processing")

    try:
        invoice = parser.parse_image(file_path)
        store.update(job_id, "completed", result=invoice)
    except Exception as e:
        store.update(job_id, "failed", error_message=str(e))
