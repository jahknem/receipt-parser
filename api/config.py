import os

MAX_FILE_SIZE_BYTES = int(os.environ.get("MAX_FILE_SIZE_BYTES", 10 * 1024 * 1024))  # 10 MB
RATE_LIMIT = os.environ.get("RATE_LIMIT", "15/minute")
