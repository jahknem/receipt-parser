import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch, MagicMock
from receipt_reader.types import Invoice, Merchant, Item, Totals
from decimal import Decimal
import time

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_parse_image():
    with patch("api.main.parse_image") as mock:
        yield mock


def test_create_receipt_and_poll_for_result(mock_parse_image):
    mock_invoice = Invoice(
        invoice_id="test_invoice",
        merchant=Merchant(name="Test Merchant", address="123 Test St"),
        timestamp="2024-01-01T00:00:00",
        currency="EUR",
        items=[
            Item(
                description="Test Item",
                qty=Decimal("1"),
                unit_price=Decimal("10.00"),
                total_price=Decimal("10.00"),
                vat_rate=19,
            )
        ],
        totals=Totals(gross=Decimal("10.00"), payment_method="card"),
        meta={},
    )
    mock_parse_image.return_value = mock_invoice

    with open("tests/rewe.png", "rb") as f:
        response = client.post("/receipts", files={"file": ("rewe.png", f, "image/png")})

    assert response.status_code == 200
    receipt_id = response.json()["receipt_id"]

    # Poll for the result
    for _ in range(10):
        response = client.get(f"/receipts/{receipt_id}")
        assert response.status_code == 200
        if response.json()["status"] == "completed":
            break
        time.sleep(0.1)

    assert response.json()["status"] == "completed"
    assert response.json()["result"]["invoice_id"] == "test_invoice"


def test_create_receipt_parsing_failure(mock_parse_image):
    mock_parse_image.side_effect = Exception("Parsing failed")

    with open("tests/rewe.png", "rb") as f:
        response = client.post("/receipts", files={"file": ("rewe.png", f, "image/png")})

    assert response.status_code == 200
    receipt_id = response.json()["receipt_id"]

    # Poll for the result
    for _ in range(10):
        response = client.get(f"/receipts/{receipt_id}")
        assert response.status_code == 200
        if response.json()["status"] == "failed":
            break
        time.sleep(0.1)

    assert response.json()["status"] == "failed"
    assert response.json()["error"] == "Parsing failed"


def test_get_nonexistent_receipt():
    response = client.get("/receipts/nonexistent_id")
    assert response.status_code == 404
