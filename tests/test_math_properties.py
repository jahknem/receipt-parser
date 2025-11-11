from decimal import Decimal


def test_item_math_holds(fixtures):
    for inv in fixtures:
        for item in inv.items:
            # unit * qty close to total (tolerate OCR rounding on source)
            expected = (item.unit_price * item.qty).quantize(Decimal("0.01"))
            assert abs(expected - item.total_price) <= Decimal("0.02"), (
                inv.invoice_id,
                item.description,
                expected,
                item.total_price,
            )
