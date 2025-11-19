import os
import tempfile
from pathlib import Path

# Storage settings
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", tempfile.gettempdir())) / "receipt-parser"
MAX_FILE_SIZE_BYTES = int(os.getenv("MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024))  # 10 MB
MAX_FILE_SIZE = MAX_FILE_SIZE_BYTES  # Alias for compatibility
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/tiff"}
RATE_LIMIT = os.environ.get("RATE_LIMIT", "15/minute")

# Create the uploads directory if it doesn't exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
