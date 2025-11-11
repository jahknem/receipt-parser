from receipt_reader.types import Invoice


def test_model_json_roundtrip(fixtures):
    for inv in fixtures:
        data = inv.json()
        again = Invoice.parse_raw(data)
        assert again.invoice_id == inv.invoice_id
        assert again.sum_items() == inv.sum_items()
