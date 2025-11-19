import json
import tempfile
import uuid
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path
from typing import Optional

import structlog
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from receipt_reader.parser import parse_image

from .config import MAX_FILE_SIZE_BYTES, RATE_LIMIT
from .jobs import Job, JobStore, timed
from .logging import setup_logging
from .metrics import instrumentator
from .storage import get_storage_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    FastAPIInstrumentor.instrument_app(app)
    yield


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
instrumentator.instrument(app)
instrumentator.expose(app)
job_store = JobStore()
storage_service = get_storage_service()
log = structlog.get_logger()


@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    request.state.logger = log.bind(correlation_id=correlation_id)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


def _parse_metadata(raw: Optional[str]) -> Optional[dict]:
    if raw in (None, ""):
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="metadata must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail="metadata must be a JSON object")
    return parsed


def _job_status_payload(job: Job) -> dict:
    payload = {"job_id": job.id, "status": job.status}
    if job.error:
        payload["error"] = job.error
    return payload


def _job_result_payload(job: Job) -> dict:
    assert job.result is not None, "job.result expected for completed jobs"
    return {
        "job_id": job.id,
        "status": "completed",
        "parsed": jsonable_encoder(job.result, custom_encoder={Decimal: str}),
        "meta": {
            "processing_time_seconds": round(job.duration_seconds or 0.0, 3),
            "model_version": "donut-base-finetuned-cord-v2",
        },
    }


def process_job(job_id: str) -> None:
    job = job_store.get(job_id)
    assert job and job.source_path, f"Job {job_id} or its source path not found"

    job_store.mark_processing(job.id)
    try:
        invoice, duration = timed(parse_image, str(job.source_path))
        job_store.mark_completed(job.id, invoice=invoice, duration=duration)
    except Exception as exc:  # pragma: no cover - defensive guard
        job_store.mark_failed(job.id, error=str(exc))
    finally:
        storage_service.cleanup(job.source_path)


@app.post("/receipts", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(RATE_LIMIT)
async def upload_receipt(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    request.state.logger.info(
        "upload_receipt",
        filename=file.filename,
        content_type=file.content_type,
        metadata=metadata,
    )
    job = job_store.create(metadata=_parse_metadata(metadata))
    job.source_path = storage_service.save_upload(job.id, file)
    background_tasks.add_task(process_job, job.id)

    status_url = str(request.url_for("get_job_status", job_id=job.id))
    result_url = str(request.url_for("get_job_result", job_id=job.id))
    headers = {"Location": result_url}
    body = {"job_id": job.id, "status_url": status_url, "estimated_seconds": 5}
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=body, headers=headers)


@app.get("/receipts/{job_id}/status")
def get_job_status(request: Request, job_id: str):
    request.state.logger.info("get_job_status", job_id=job_id)
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_status_payload(job)


@app.get("/receipts/{job_id}")
def get_job_result(request: Request, job_id: str):
    request.state.logger.info("get_job_result", job_id=job_id)
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "completed":
        return _job_result_payload(job)
    if job.status == "failed":
        raise HTTPException(status_code=500, detail=job.error or "Parsing failed")

    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content=_job_status_payload(job),
    )


app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
