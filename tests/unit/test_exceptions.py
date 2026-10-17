from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from echovault.core.exceptions import (
    ErrorCode,
    InvalidRequestError,
    ProjectAccessDeniedError,
    ResourceNotFoundError,
    VersionConflictError,
)
from echovault.main import create_app


class ItemPayload(BaseModel):
    name: str
    count: int


custom_router = APIRouter()


@custom_router.get("/test/custom-error")
def raise_custom_error() -> None:
    raise ResourceNotFoundError("Specific resource was not found.")


@custom_router.get("/test/version-conflict")
def raise_version_conflict() -> None:
    raise VersionConflictError("Memory has been updated by another client.")


@custom_router.get("/test/invalid-request")
def raise_invalid_request() -> None:
    raise InvalidRequestError("Malformed query filter.")


@custom_router.get("/test/access-denied")
def raise_access_denied() -> None:
    raise ProjectAccessDeniedError("Access to project 'proj_123' denied.")


@custom_router.get("/test/starlette-http-error")
def raise_starlette_error() -> None:
    raise StarletteHTTPException(status_code=403, detail="Forbidden action")


@custom_router.get("/test/unhandled-error")
def raise_unhandled_error() -> None:
    raise RuntimeError("sensitive internal failure: secret_db_key=12345")


@custom_router.post("/test/validation")
def validate_body(payload: ItemPayload) -> dict[str, str]:
    return {"status": "ok"}


def create_test_client() -> TestClient:
    app = create_app()
    app.include_router(custom_router)
    return TestClient(app, raise_server_exceptions=False)


def test_resource_not_found_error_format() -> None:
    client = create_test_client()
    response = client.get("/test/custom-error", headers={"X-Request-ID": "req_test123"})
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == ErrorCode.RESOURCE_NOT_FOUND
    assert data["error"]["message"] == "Specific resource was not found."
    assert data["error"]["request_id"] == "req_test123"
    assert response.headers.get("X-Request-ID") == "req_test123"


def test_version_conflict_error_format() -> None:
    client = create_test_client()
    response = client.get("/test/version-conflict")
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == ErrorCode.VERSION_CONFLICT
    assert data["error"]["message"] == "Memory has been updated by another client."
    assert data["error"]["request_id"].startswith("req_")


def test_access_denied_error_format() -> None:
    client = create_test_client()
    response = client.get("/test/access-denied")
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == ErrorCode.PROJECT_ACCESS_DENIED


def test_starlette_http_exception_mapping() -> None:
    client = create_test_client()
    response = client.get("/test/starlette-http-error")
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == ErrorCode.PROJECT_ACCESS_DENIED
    assert data["error"]["message"] == "Forbidden action"


def test_validation_error_format() -> None:
    client = create_test_client()
    response = client.post("/test/validation", json={"name": "test", "count": "not-an-int"})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == ErrorCode.VALIDATION_ERROR
    assert "Validation failed" in data["error"]["message"]
    assert "request_id" in data["error"]


def test_unhandled_exception_does_not_leak_internals() -> None:
    client = create_test_client()
    response = client.get("/test/unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == ErrorCode.INTERNAL_ERROR
    assert data["error"]["message"] == "An unexpected internal server error occurred."
    assert "secret_db_key" not in response.text
    assert "RuntimeError" not in response.text
    assert "Traceback" not in response.text
