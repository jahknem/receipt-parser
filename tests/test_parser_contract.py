import pytest
from receipt_reader import parser


@pytest.mark.parametrize(
    "path", [
        "tests/toom.png",
        "tests/tegut.png",
        "tests/jacques.png",
        "tests/rewe.png",
        "tests/rewe2.png",
    ]
)
def test_parse_image_contract(path):
    # This asserts the function exists and raises NotImplementedError until implemented
    parser.parse_image(path)
