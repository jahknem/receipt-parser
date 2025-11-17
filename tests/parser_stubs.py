"""
Fixtures and stubs for testing the parser.
"""
from __future__ import annotations
import json
from types import SimpleNamespace
from decimal import Decimal
import datetime

from receipt_reader.types import Invoice, Merchant, Item, Totals
from receipt_reader import parser


class _FakeTensor:  # pragma: no cover
    def to(self, device: str) -> "_FakeTensor":
        return self


class _FakeTokenizer:  # pragma: no cover
    def __call__(self, *_, **__) -> SimpleNamespace:
        return SimpleNamespace(input_ids=_FakeTensor())

    @property
    def pad_token_id(self) -> int:
        return 0

    @property
    def eos_token_id(self) -> int:
        return 1

    @property
    def unk_token_id(self) -> int:
        return 2

    @property
    def eos_token(self) -> str:
        return "</s>"

    @property
    def pad_token(self) -> str:
        return "<pad>"


def stub_donut_pipeline(monkeypatch, *, raw_sequence: str) -> None:
    """Monkeypatch the heavy Donut model/procesor/image stack with lightweight fakes."""

    class _FakeProcessor:
        def __init__(self) -> None:
            self._sequence = f"<s_cord-v2>{raw_sequence}"
            self.tokenizer = _FakeTokenizer()

        def __call__(self, *_, **__) -> SimpleNamespace:
            return SimpleNamespace(pixel_values=_FakeTensor())

        def batch_decode(self, sequences):
            return [self._sequence]

        @classmethod
        def from_pretrained(cls, *args, **kwargs):  # pragma: no cover - trivial path
            return cls()

    class _FakeModel:
        decoder = SimpleNamespace(config=SimpleNamespace(max_position_embeddings=128))

        def to(self, device: str) -> "_FakeModel":  # pragma: no cover
            return self

        @classmethod
        def from_pretrained(cls, *args, **kwargs):  # pragma: no cover
            return cls()

        def generate(self, *args, **kwargs):
            return SimpleNamespace(sequences=["unused"])

        def parameters(self):
            return [SimpleNamespace(device="cpu")]

    monkeypatch.setattr("transformers.DonutProcessor", _FakeProcessor)
    monkeypatch.setattr("transformers.VisionEncoderDecoderModel", _FakeModel)
    monkeypatch.setattr("PIL.Image.open", lambda _: SimpleNamespace(convert=lambda _: None))


def invoice_to_sequence(invoice: Invoice) -> str:
    """
    Very basic implementation to convert an invoice to a sequence string.
    This is not a robust implementation and only covers the fields used in the test fixtures.
    """
    data = {
        "merchant_name": {"value": invoice.merchant.name},
        "merchant_address": {"value": invoice.merchant.address},
        "menu": [
            {
                "nm": {"value": item.description},
                "cnt": {"value": str(item.qty)},
                "price": {"value": str(item.unit_price)},
            }
            for item in invoice.items
        ],
        "total": {"price": {"value": str(invoice.totals.gross)}},
    }
    return json.dumps(data, ensure_ascii=False)


_FIXTURES = [
    Invoice(
        invoice_id="toom-2025-08-07-1601",
        merchant=Merchant(
            name="toom Baumarkt",
            address="61169 Friedberg",
            phone="+49 6031 68430",
        ),
        timestamp=datetime.datetime(2025, 8, 7, 16, 1, 31).isoformat(),
        items=[
            Item(
                description="H-Milch 3,5% 1l",
                qty=Decimal("2"),
                unit_price=Decimal("1.19"),
                total_price=Decimal("2.38"),
                vat_rate=7,
            ),
            Item(
                description="ES Tomaten Ketchup",
                qty=Decimal("1"),
                unit_price=Decimal("2.29"),
                total_price=Decimal("2.29"),
                vat_rate=7,
            ),
        ],
        totals=Totals(
            gross=Decimal("4.67"),
            payment_method="Girocard",
        ),
        meta={"source_image": "tests/toom.png"},
    ),
    Invoice(
        invoice_id="tegut-2025-08-07-2001",
        merchant=Merchant(
            name="tegut",
            address="61169 Friedberg",
            phone="+49 6031 685360",
        ),
        timestamp=datetime.datetime(2025, 8, 7, 20, 1, 12).isoformat(),
        items=[
            Item(
                description="Bio-Zitronen",
                qty=Decimal("1"),
                unit_price=Decimal("1.99"),
                total_price=Decimal("1.99"),
                vat_rate=7,
            ),
            Item(
                description="Bio-Ingwer",
                qty=Decimal("0.082"),
                unit_price=Decimal("14.90"),
                total_price=Decimal("1.22"),
                vat_rate=7,
            ),
            Item(
                description="Landliebe Butter",
                qty=Decimal("1"),
                unit_price=Decimal("2.29"),
                total_price=Decimal("2.29"),
                vat_rate=7,
            ),
        ],
        totals=Totals(
            gross=Decimal("5.50"),
            payment_method="Girocard",
        ),
        meta={"source_image": "tests/tegut.png"},
    ),
    Invoice(
        invoice_id="jacques-2025-08-07-2032",
        merchant=Merchant(
            name="Jacques' Wein-Depot",
            address="61169 Friedberg",
            phone="+49 6031 166793",
        ),
        timestamp=datetime.datetime(2025, 8, 7, 20, 32, 5).isoformat(),
        items=[
            Item(
                description="2022 Velarino",
                qty=Decimal("1"),
                unit_price=Decimal("6.95"),
                total_price=Decimal("6.95"),
                vat_rate=19,
            ),
            Item(
                description="2022 L'Emage",
                qty=Decimal("1"),
                unit_price=Decimal("6.95"),
                total_price=Decimal("6.95"),
                vat_rate=19,
            ),
        ],
        totals=Totals(
            gross=Decimal("13.90"),
            payment_method="Visa",
        ),
        meta={"source_image": "tests/jacques.png"},
    ),
    Invoice(
        invoice_id="rewe-2025-08-07-2045",
        merchant=Merchant(
            name="REWE",
            address="61169 Friedberg",
            phone=None,
        ),
        timestamp=datetime.datetime(2025, 8, 7, 20, 45, 12).isoformat(),
        items=[
            Item(
                description="Pfanner Eistee",
                qty=Decimal("1"),
                unit_price=Decimal("1.99"),
                total_price=Decimal("1.99"),
                vat_rate=19,
            ),
            Item(
                description="ja! Flips",
                qty=Decimal("1"),
                unit_price=Decimal("0.99"),
                total_price=Decimal("0.99"),
                vat_rate=7,
            ),
        ],
        totals=Totals(
            gross=Decimal("2.98"),
            payment_method="Girocard",
        ),
        meta={"source_image": "tests/rewe.png"},
    ),
    Invoice(
        invoice_id="rewe-2025-08-07-2102",
        merchant=Merchant(
            name="REWE – Im Krämer",
            address="61169 Friedberg",
            phone=None,
        ),
        timestamp=datetime.datetime(2025, 8, 7, 21, 2, 41).isoformat(),
        items=[
            Item(
                description="Pfand",
                qty=Decimal("2"),
                unit_price=Decimal("0.25"),
                total_price=Decimal("0.50"),
                vat_rate=0,
            ),
            Item(
                description="Bananen",
                qty=Decimal("0.534"),
                unit_price=Decimal("1.69"),
                total_price=Decimal("0.90"),
                vat_rate=7,
            ),
            Item(
                description="Zucchini lose",
                qty=Decimal("0.342"),
                unit_price=Decimal("2.49"),
                total_price=Decimal("0.85"),
                vat_rate=7,
            ),
            Item(
                description="ja! Weizenmehl",
                qty=Decimal("1"),
                unit_price=Decimal("0.69"),
                total_price=Decimal("0.69"),
                vat_rate=7,
            ),
            Item(
                description="Alpro Soja Drink",
                qty=Decimal("1"),
                unit_price=Decimal("2.29"),
                total_price=Decimal("2.29"),
                vat_rate=7,
            ),
            Item(
                description="Alpro Soja Joghurt",
                qty=Decimal("1"),
                unit_price=Decimal("1.99"),
                total_price=Decimal("1.99"),
                vat_rate=7,
            ),
            Item(
                description="REWE Bio Tofu",
                qty=Decimal("1"),
                unit_price=Decimal("1.99"),
                total_price=Decimal("1.99"),
                vat_rate=7,
            ),
            Item(
                description="REWE Bio Paprika",
                qty=Decimal("1"),
                unit_price=Decimal("3.49"),
                total_price=Decimal("3.49"),
                vat_rate=7,
            ),
        ],
        totals=Totals(
            gross=Decimal("12.26"),
            payment_method="Cash (20.00 given, 7.74 change)",
        ),
        meta={"source_image": "tests/rewe2.png"},
    ),
]

ALL_FIXTURES = sorted(_FIXTURES, key=lambda i: i.invoice_id)
