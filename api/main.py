from fastapi import FastAPI, File, UploadFile
from receipt_reader.parser import parse_image
from receipt_reader.types import Invoice
import shutil
import tempfile
import os

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.post("/parse-receipt/", response_model=Invoice)
async def parse_receipt_image(file: UploadFile = File(...)):
    """
    Parses a receipt image and returns the extracted invoice data.
    """
    try:
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
    finally:
        file.file.close()

    try:
        # Parse the image
        invoice = parse_image(tmp_path)
        return invoice
    finally:
        # Clean up the temporary file
        os.unlink(tmp_path)
