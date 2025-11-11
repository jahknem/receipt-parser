from decimal import Decimal
from receipt_reader.types import Invoice


def test_fixtures_are_valid_invoices(fixtures):
    # Pydantic validation already occurred on construction; just ensure types and simple invariants
    for inv in fixtures:
        assert isinstance(inv, Invoice)
        assert inv.currency == "EUR"
        assert inv.items, f"{inv.invoice_id} has no items"
        # Sum of items should equal gross within 0.02 tolerance
        total = inv.sum_items()
        assert abs(total - inv.totals.gross) <= Decimal("0.02"), (
            inv.invoice_id,
            total,
            inv.totals.gross,
        )
        # VAT sanity: all vat_rate in {7, 19}
        assert {i.vat_rate for i in inv.items}.issubset({7, 19})
