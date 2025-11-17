import json
import time
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from api import main
from receipt_reader.types import Invoice, Item, Merchant, Totals

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_state(monkeypatch, tmp_path):
    main.job_store.reset()
    monkeypatch.setattr(main, "UPLOADS_DIR", tmp_path)
    main.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    yield
    main.job_store.reset()


def sample_invoice():
    return Invoice(
        invoice_id="test_invoice",
        merchant=Merchant(name="Test Merchant", address="123 Test St"),
        timestamp="2024-01-01T00:00:00",
        currency="EUR",
        items=[
            Item(
                sku_or_ean=None,
                description="Test Item",
                qty=Decimal("1"),
                unit_price=Decimal("10.00"),
                total_price=Decimal("10.00"),
                vat_rate=19,
                confidence=1.0,
            )
        ],
        totals=Totals(gross=Decimal("10.00"), payment_method="card"),
        meta={},
    )


def _file_payload():
    return {"file": ("receipt.png", b"fake-bytes", "image/png")}


def _wait_for_status(job_id: str) -> dict:
    payload: dict = {}
    for _ in range(10):
        status_response = client.get(f"/receipts/{job_id}/status")
        payload = status_response.json()
        if payload["status"] in {"completed", "failed"}:
            return payload
        time.sleep(0.02)
    return payload


def test_async_flow_returns_completed_result(monkeypatch):
    monkeypatch.setattr(main, "parse_image", lambda path: sample_invoice())

    response = client.post(
        "/receipts",
        files=_file_payload(),
        data={"metadata": json.dumps({"source": "mobile"})},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert response.json()["status_url"].endswith(f"/receipts/{job_id}/status")
    assert response.headers["Location"].endswith(f"/receipts/{job_id}")

    status_payload = _wait_for_status(job_id)
    assert status_payload["status"] == "completed"

    result_response = client.get(f"/receipts/{job_id}")
    assert result_response.status_code == 200
    assert result_response.json()["parsed"]["merchant"]["name"] == "Test Merchant"


def test_sync_flow_returns_parse_result(monkeypatch):
    monkeypatch.setattr(main, "parse_image", lambda path: sample_invoice())

    response = client.post(
        "/receipts",
        params={"sync": "true"},
        files=_file_payload(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["parsed"]["merchant"]["name"] == "Test Merchant"


def test_metadata_validation_error(monkeypatch):
    monkeypatch.setattr(main, "parse_image", lambda path: sample_invoice())

    response = client.post(
        "/receipts",
        files=_file_payload(),
        data={"metadata": "not-json"},
    )

    assert response.status_code == 400


def test_failed_job_returns_error(monkeypatch):
    def _raise(path):
        raise RuntimeError("Parsing failed")

    monkeypatch.setattr(main, "parse_image", _raise)

    response = client.post("/receipts", files=_file_payload())
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    status_payload = _wait_for_status(job_id)
    assert status_payload["status"] == "failed"

    result_response = client.get(f"/receipts/{job_id}")
    assert result_response.status_code == 500
    assert result_response.json()["detail"] == "Parsing failed"


def test_unknown_job_returns_404():
    assert client.get("/receipts/missing/status").status_code == 404
    assert client.get("/receipts/missing").status_code == 404
