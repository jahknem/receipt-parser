import os
import tempfile
from pathlib import Path

# Storage settings
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", tempfile.gettempdir())) / "receipt-parser"
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10 MB
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/tiff"}

# Create the uploads directory if it doesn't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
