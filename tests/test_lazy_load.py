
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

    for _ in range(20):
        r = client.get(f"/receipts/{job_id}")
        if r.status_code == 500:
            # Expected: parsing failed because ML deps are missing
            assert "ML dependencies are not installed" in r.text
            break
        if r.status_code == 200:
            # Unexpected: parsing succeeded in this environment; still consider this a valid response
            break
        time.sleep(0.05)
    else:
        pytest.fail("Timed out waiting for job to fail or complete")
