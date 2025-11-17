
import sys
import time
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.main import app, job_store

client = TestClient(app)


def _assert_is_job_id(payload: dict) -> None:
    assert "job_id" in payload
    assert isinstance(payload["job_id"], str)
    assert len(payload["job_id"]) > 5


def test_upload_receipt_without_model_dependencies(monkeypatch):
    """Test that uploading a receipt without the ML dependencies returns a helpful error."""
    # Temporarily remove torch and transformers from sys.modules to simulate them not being installed
    monkeypatch.setitem(sys.modules, "torch", None)
    monkeypatch.setitem(sys.modules, "transformers", None)

    # Reset the parser's model cache to force it to try and reload the model
    from receipt_reader import parser
    parser._processor = None
    parser._model = None

    with open("tests/rewe.png", "rb") as f:
        response = client.post("/receipts", files={"file": ("rewe.png", f, "image/png")})

    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # Poll for job completion
    for _ in range(10):
        time.sleep(0.1)
        status_response = client.get(f"/receipts/{job_id}/status")
        if status_response.json()["status"] in ("completed", "failed"):
            break

    result_response = client.get(f"/receipts/{job_id}")
    assert result_response.status_code == 500
    assert "ML dependencies are not installed" in result_response.text
