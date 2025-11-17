from fastapi import FastAPI, File, UploadFile, HTTPException
from receipt_reader.parser import parse_image
import uuid
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are supported.")

    file_extension = file.filename.split(".")[-1]
    temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"

    with open(temp_file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        invoice_data = parse_image(temp_file_path)
    finally:
        os.remove(temp_file_path)

    return invoice_data
