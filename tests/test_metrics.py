import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_metrics_endpoint(client):
    """
    Tests that the /metrics endpoint returns the expected metrics.
    """
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "receipt_parser_job_queue_depth" in response.text
