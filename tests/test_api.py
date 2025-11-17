import pytest
from fastapi.testclient import TestClient
from api.main import app
from unittest.mock import patch
from receipt_reader.types import Invoice, Merchant, Item, Totals
from decimal import Decimal
import os
from PIL import Image

client = TestClient(app)


def test_upload_receipt_success():
    with patch("api.main.parse_image") as mock_parse_image:
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
            response = client.post("/upload", files={"file": ("rewe.png", f, "image/png")})

    assert response.status_code == 200
    assert response.json()["invoice_id"] == "test_invoice"


def test_upload_receipt_invalid_file_type():
    with open("tests/rewe.json", "rb") as f:
        response = client.post("/upload", files={"file": ("rewe.json", f, "application/json")})

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid file type. Only JPEG and PNG are supported."}


def test_upload_receipt_parsing_failure():
    with patch("api.main.parse_image") as mock_parse_image:
        mock_parse_image.side_effect = Exception("Parsing failed")

        with open("tests/rewe.png", "rb") as f:
            with pytest.raises(Exception) as excinfo:
                client.post("/upload", files={"file": ("rewe.png", f, "image/png")})

        assert "Parsing failed" in str(excinfo.value)


def test_upload_receipt_empty_file():
    img = Image.new('RGB', (10, 10))
    img.save("empty.png", "PNG")

    with open("empty.png", "rb") as f:
        response = client.post("/upload", files={"file": ("empty.png", f, "image/png")})

    assert response.status_code == 200
    assert response.json()["merchant"]["name"] == "unknown"

    os.remove("empty.png")
