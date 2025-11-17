import json
import tempfile
from pathlib import Path
from typing import Optional

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
from fastapi.responses import JSONResponse

from receipt_reader.parser import parse_image

from .jobs import Job, JobStore, timed

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/tiff"}
UPLOADS_DIR = Path(tempfile.gettempdir()) / "receipt-parser"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
job_store = JobStore()


def _validate_content_type(upload: UploadFile) -> None:
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG or TIFF are supported.")


async def _persist_upload(job: Job, upload: UploadFile) -> Path:
    _validate_content_type(upload)
    suffix = Path(upload.filename or "receipt").suffix or ".png"
    destination = UPLOADS_DIR / f"{job.id}{suffix}"
    data = await upload.read()
    with destination.open("wb") as fh:
        fh.write(data)
    upload.file.close()
    return destination


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
        "parsed": job.result.dict(),
        "meta": {
            "processing_time_seconds": round(job.duration_seconds or 0.0, 3),
            "model_version": "donut-base-finetuned-cord-v2",
        },
    }


def process_job(job_id: str, file_path: str) -> None:
    job_store.mark_processing(job_id)
    try:
        invoice, duration = timed(parse_image, file_path)
        job_store.mark_completed(job_id, invoice=invoice, duration=duration)
    except Exception as exc:  # pragma: no cover - defensive guard
        job_store.mark_failed(job_id, error=str(exc))
    finally:
        Path(file_path).unlink(missing_ok=True)


@app.post("/receipts", status_code=status.HTTP_202_ACCEPTED)
async def upload_receipt(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    metadata: Optional[str] = Form(None),
):
    job = job_store.create(metadata=_parse_metadata(metadata))
    stored_file = await _persist_upload(job, file)
    background_tasks.add_task(process_job, job.id, str(stored_file))

    status_url = str(request.url_for("get_job_status", job_id=job.id))
    result_url = str(request.url_for("get_job_result", job_id=job.id))
    headers = {"Location": result_url}
    body = {"job_id": job.id, "status_url": status_url, "estimated_seconds": 5}
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=body, headers=headers)


@app.get("/receipts/{job_id}/status")
def get_job_status(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_status_payload(job)


@app.get("/receipts/{job_id}")
def get_job_result(job_id: str):
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
