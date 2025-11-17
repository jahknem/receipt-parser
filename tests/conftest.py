import pytest
from tests.fixtures_data import ALL_FIXTURES


@pytest.fixture(scope="session")
def fixtures():
    return ALL_FIXTURES
