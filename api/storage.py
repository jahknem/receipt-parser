from __future__ import annotations
import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from . import config

class StorageService:
    def __init__(self, uploads_dir: Path):
        self._uploads_dir = uploads_dir
        self._uploads_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, job_id: str, upload: UploadFile) -> Path:
        self._validate_content_type(upload)
        suffix = Path(upload.filename or "receipt").suffix or ".png"
        destination = self._uploads_dir / f"{job_id}{suffix}"

        try:
            self._stream_to_disk(upload, destination)
        except Exception as exc:
            destination.unlink(missing_ok=True)
            raise exc

        return destination

    @staticmethod
    def cleanup(file_path: str | Path) -> None:
        Path(file_path).unlink(missing_ok=True)

    def _validate_content_type(self, upload: UploadFile) -> None:
        if upload.content_type not in config.ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

    def _stream_to_disk(self, upload: UploadFile, destination: Path) -> None:
        size = 0
        with destination.open("wb") as fh:
            while chunk := upload.file.read(4096):
                size += len(chunk)
                if size > config.MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File size exceeds limit of {config.MAX_FILE_SIZE / 1024 / 1024:.0f} MB",
                    )
                fh.write(chunk)

def get_storage_service() -> StorageService:
    """Factory to create a StorageService with the latest config."""
    return StorageService(config.UPLOADS_DIR)
