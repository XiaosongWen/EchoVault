from fastapi.testclient import TestClient

from echovault.core.context import generate_request_id, get_request_id, set_request_id
from echovault.main import app

client = TestClient(app)


def test_request_id_propagates_from_client() -> None:
    custom_id = "req_custom-abc_123"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


def test_request_id_generated_when_missing() -> None:
    response = client.get("/health")
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
    assert req_id.startswith("req_")


def test_malformed_request_id_is_replaced() -> None:
    malformed_id = "req_bad;drop table users;--"
    response = client.get("/health", headers={"X-Request-ID": malformed_id})
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
    assert req_id != malformed_id
    assert req_id.startswith("req_")


def test_context_get_and_set() -> None:
    sample_id = generate_request_id()
    assert sample_id.startswith("req_")
    set_request_id(sample_id)
    assert get_request_id() == sample_id
