from decimal import Decimal
import pytest

from receipt_reader import parser
from tests.fixtures_data import ALL_FIXTURES


@pytest.mark.parametrize("fixture", ALL_FIXTURES)
def test_parse_image_matches_fixture(fixture):
    """Integration-style tests: parse the image and compare core fields to the fixture.

    This is intentionally a high-level contract test to drive parser implementation.
    The parser is expected to return a `receipt_reader.types.Invoice` instance with
    matching invoice_id, merchant name, number of items, and item totals (within
    a small rounding tolerance).
    """
    path = fixture.meta.get("source_image")
    assert path, f"fixture {fixture.invoice_id} missing source_image"

    parsed = parser.parse_image(path)

    # Basic identity
    assert parsed.invoice_id == fixture.invoice_id
    assert parsed.currency == fixture.currency
    assert parsed.merchant.name == fixture.merchant.name

    # Items and sums
    assert len(parsed.items) == len(fixture.items), (
        fixture.invoice_id,
        len(parsed.items),
        len(fixture.items),
    )
    assert parsed.sum_items() == fixture.sum_items()

    # Per-item checks: description and total_price (allow small rounding tolerance)
    for expected_item, parsed_item in zip(fixture.items, parsed.items):
        assert parsed_item.description == expected_item.description
        assert abs(parsed_item.total_price - expected_item.total_price) <= Decimal("0.02"), (
            fixture.invoice_id,
            expected_item.description,
            parsed_item.total_price,
            expected_item.total_price,
        )
