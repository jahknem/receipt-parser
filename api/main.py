from fastapi import FastAPI, File, UploadFile, HTTPException
from receipt_reader.parser import parse_image
import uuid
import os
import threading
from typing import Dict

app = FastAPI()

jobs: Dict[str, Dict] = {}


def process_receipt(receipt_id: str, temp_file_path: str):
    try:
        invoice_data = parse_image(temp_file_path)
        jobs[receipt_id]["status"] = "completed"
        jobs[receipt_id]["result"] = invoice_data.dict()
    except Exception as e:
        jobs[receipt_id]["status"] = "failed"
        jobs[receipt_id]["error"] = str(e)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/receipts")
async def create_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")

    file_extension = file.filename.split(".")[-1]
    receipt_id = str(uuid.uuid4())
    temp_file_path = f"/tmp/{receipt_id}.{file_extension}"

    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    jobs[receipt_id] = {"status": "pending"}

    thread = threading.Thread(target=process_receipt, args=(receipt_id, temp_file_path))
    thread.start()

    return {"receipt_id": receipt_id}


@app.get("/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    job = jobs.get(receipt_id)
    if not job:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return job
