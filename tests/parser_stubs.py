"""Test helpers for stubbing the Donut pipeline used by `receipt_reader.parser`."""
from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Dict

from receipt_reader import parser


class _FakeTensor:
    def to(self, device: str) -> "_FakeTensor":  # pragma: no cover - trivial helper
        return self


class _FakeTokenizer:
    pad_token_id = 0
    eos_token_id = 1
    unk_token_id = 2
    pad_token = "<pad>"
    eos_token = "</eos>"

    def __call__(self, *args: Any, **kwargs: Any) -> SimpleNamespace:
        return SimpleNamespace(input_ids=_FakeTensor())


class _FakeImage:
    def convert(self, *_: Any) -> "_FakeImage":  # pragma: no cover
        return self


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

    monkeypatch.setattr(parser, "DonutProcessor", _FakeProcessor)
    monkeypatch.setattr(parser, "VisionEncoderDecoderModel", _FakeModel)
    monkeypatch.setattr(parser.Image, "open", lambda path: _FakeImage())


def invoice_to_sequence(invoice) -> str:
    """Convert a fixture Invoice into the pseudo-Donut JSON sequence the parser expects."""

    def _wrap(value: Any) -> Dict[str, Any]:
        return {"value": value}

    menu = []
    for item in invoice.items:
        menu.append(
            {
                "nm": _wrap(item.description),
                "cnt": _wrap(str(item.qty)),
                "price": _wrap(str(item.unit_price)),
            }
        )

    payload: Dict[str, Any] = {
        "merchant_name": _wrap(invoice.merchant.name),
        "merchant_address": _wrap(invoice.merchant.address),
        "menu": menu,
        "total": {"price": _wrap(str(invoice.totals.gross))},
    }

    return json.dumps(payload, ensure_ascii=False)
