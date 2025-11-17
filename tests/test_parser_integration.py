from decimal import Decimal
import json

import pytest

from receipt_reader import parser
from tests.fixtures_data import ALL_FIXTURES
from tests import parser_stubs


@pytest.mark.parametrize("fixture", ALL_FIXTURES)
def test_parse_image_with_stubbed_pipeline_matches_fixture(monkeypatch, fixture):
    """Simulate the full Donut pipeline so we can assert parse_image against our fixtures."""

    sequence = parser_stubs.invoice_to_sequence(fixture)
    parser_stubs.stub_donut_pipeline(monkeypatch, raw_sequence=sequence)

    parsed = parser.parse_image("tests/dummy.png")

    assert parsed.currency == fixture.currency
    assert parsed.merchant.name == fixture.merchant.name
    assert len(parsed.items) == len(fixture.items)
    assert parsed.sum_items() == fixture.sum_items()

    for expected_item, parsed_item in zip(fixture.items, parsed.items):
        assert parsed_item.description == expected_item.description
        assert parsed_item.qty == expected_item.qty
        assert abs(parsed_item.total_price - expected_item.total_price) <= Decimal("0.02")


def test_parse_image_returns_unknown_invoice_on_invalid_json(monkeypatch):
    parser_stubs.stub_donut_pipeline(monkeypatch, raw_sequence="{not-json")

    parsed = parser.parse_image("tests/invalid.png")

    assert parsed.invoice_id == "unknown"
    assert parsed.merchant.name == "unknown"
    assert parsed.totals.gross == Decimal("0")
    assert parsed.items == []


def test_parse_image_skips_items_with_missing_values(monkeypatch):
    payload = {
        "merchant_name": {"value": "Demo Shop"},
        "merchant_address": {"value": "123 Demo St"},
        "menu": [
            {
                "nm": {"value": "Broken Item"},
                "cnt": {"value": None},
                "price": {"value": "1.23"},
            }
        ],
        "total": {"price": {"value": "0"}},
    }

    parser_stubs.stub_donut_pipeline(monkeypatch, raw_sequence=json.dumps(payload, ensure_ascii=False))

    parsed = parser.parse_image("tests/broken.png")

    assert parsed.merchant.name == "Demo Shop"
    assert parsed.items == []
