import json

import pytest
from receipt_reader import parser
from tests import parser_stubs


@pytest.mark.parametrize(
    "path", [
        "tests/toom.png",
        "tests/tegut.png",
        "tests/jacques.png",
        "tests/rewe.png",
        "tests/rewe2.png",
    ]
)
def test_parse_image_contract(monkeypatch, path):
    payload = {
        "merchant_name": {"value": "Contract Store"},
        "merchant_address": {"value": "Unknown"},
        "menu": [],
        "total": {"price": {"value": "0"}},
    }

    parser_stubs.stub_donut_pipeline(monkeypatch, raw_sequence=json.dumps(payload))

    parser.parse_image(path)
