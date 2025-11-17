from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import shutil
import os
from . import jobs
from .jobs import JobStatus

app = FastAPI()

# Create a directory for uploads
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/receipts", status_code=202)
async def upload_receipt(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    job = jobs.get_store().create()
    file_path = os.path.join(UPLOADS_DIR, f"{job.id}_{file.filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    background_tasks.add_task(jobs.process_job, job.id, file_path)

    return {"job_id": job.id}


@app.get("/receipts/{job_id}/status")
def get_job_status(job_id: str):
    job = jobs.get_store().get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": job.status}


@app.get("/receipts/{job_id}")
def get_job_result(job_id: str):
    job = jobs.get_store().get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "completed":
        return JSONResponse(status_code=200, content=jsonable_encoder(job.result))
    elif job.status == "failed":
        return JSONResponse(
            status_code=500, content={"error": job.error_message}
        )
    else:
        return JSONResponse(status_code=202, content={"status": job.status})
