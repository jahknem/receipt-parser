from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app
from receipt_reader.types import Invoice, Merchant, Totals
from decimal import Decimal

client = TestClient(app)


def test_upload_receipt():
    with patch("api.jobs.process_job") as mock_process_job:
        with open("tests/rewe.png", "rb") as f:
            response = client.post("/receipts", files={"file": ("rewe.png", f, "image/png")})

        assert response.status_code == 202
        assert "job_id" in response.json()
        job_id = response.json()["job_id"]
        mock_process_job.assert_called_once()


def test_get_job_status():
    with patch("api.jobs.get_store") as mock_get_store:
        mock_job = MagicMock()
        mock_job.status = "processing"
        mock_get_store.return_value.get.return_value = mock_job

        response = client.get("/receipts/some_job_id/status")
        assert response.status_code == 200
        assert response.json() == {"status": "processing"}


def test_get_job_result_completed():
    with patch("api.jobs.get_store") as mock_get_store:
        mock_invoice = Invoice(
            invoice_id="123",
            merchant=Merchant(name="Test Merchant", address="123 Test St"),
            timestamp="2023-01-01T00:00:00",
            items=[],
            totals=Totals(gross=Decimal("10.00"), payment_method="card"),
            meta={},
        )
        mock_job = MagicMock()
        mock_job.status = "completed"
        mock_job.result = mock_invoice
        mock_get_store.return_value.get.return_value = mock_job

        from fastapi.encoders import jsonable_encoder
        response = client.get("/receipts/some_job_id")
        assert response.status_code == 200
        assert response.json() == jsonable_encoder(mock_invoice)


def test_get_job_result_failed():
    with patch("api.jobs.get_store") as mock_get_store:
        mock_job = MagicMock()
        mock_job.status = "failed"
        mock_job.error_message = "Parsing failed"
        mock_get_store.return_value.get.return_value = mock_job

        response = client.get("/receipts/some_job_id")
        assert response.status_code == 500
        assert response.json() == {"error": "Parsing failed"}


def test_get_job_result_pending():
    with patch("api.jobs.get_store") as mock_get_store:
        mock_job = MagicMock()
        mock_job.status = "pending"
        mock_get_store.return_value.get.return_value = mock_job

        response = client.get("/receipts/some_job_id")
        assert response.status_code == 202
        assert response.json() == {"status": "pending"}
