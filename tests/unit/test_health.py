from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from echovault.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_ready_success() -> None:
    with patch(
        "echovault.api.health.check_database_connection",
        new_callable=AsyncMock,
        return_value=(True, "ok"),
    ):
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {
            "status": "ready",
            "checks": {"database": "ok"},
        }
        assert "X-Request-ID" in response.headers


def test_ready_failure_returns_503() -> None:
    with patch(
        "echovault.api.health.check_database_connection",
        new_callable=AsyncMock,
        return_value=(False, "unavailable"),
    ):
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.json() == {
            "status": "not_ready",
            "checks": {"database": "unavailable"},
        }
        assert "X-Request-ID" in response.headers
