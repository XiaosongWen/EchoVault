from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    PROJECT_ACCESS_DENIED = "PROJECT_ACCESS_DENIED"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    TOPIC_ALREADY_EXISTS = "TOPIC_ALREADY_EXISTS"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


class EchoVaultError(Exception):
    """Base exception for all application errors."""

    status_code: int = 500
    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    message: str = "An unexpected error occurred."

    def __init__(
        self,
        message: str | None = None,
        *,
        code: ErrorCode | None = None,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class InvalidRequestError(EchoVaultError):
    status_code = 400
    code = ErrorCode.INVALID_REQUEST
    message = "Invalid request parameters or malformed input."


class UnauthorizedError(EchoVaultError):
    status_code = 401
    code = ErrorCode.UNAUTHORIZED
    message = "Missing, invalid, or expired authentication credentials."


class ProjectAccessDeniedError(EchoVaultError):
    status_code = 403
    code = ErrorCode.PROJECT_ACCESS_DENIED
    message = "The caller lacks permission to access the project."


class ResourceNotFoundError(EchoVaultError):
    status_code = 404
    code = ErrorCode.RESOURCE_NOT_FOUND
    message = "The requested resource was not found."


class VersionConflictError(EchoVaultError):
    status_code = 409
    code = ErrorCode.VERSION_CONFLICT
    message = "The resource version has changed since it was read."


class TopicAlreadyExistsError(EchoVaultError):
    status_code = 409
    code = ErrorCode.TOPIC_ALREADY_EXISTS
    message = "A memory with the same topic already exists in the project."


class PayloadTooLargeError(EchoVaultError):
    status_code = 413
    code = ErrorCode.PAYLOAD_TOO_LARGE
    message = "The request exceeds the configured payload limit."


class ValidationError(EchoVaultError):
    status_code = 422
    code = ErrorCode.VALIDATION_ERROR
    message = "Content validation or schema validation failed."


class RateLimitedError(EchoVaultError):
    status_code = 429
    code = ErrorCode.RATE_LIMITED
    message = "The caller exceeded the allowed request rate."


class InternalError(EchoVaultError):
    status_code = 500
    code = ErrorCode.INTERNAL_ERROR
    message = "An unexpected internal server error occurred."


class ServiceUnavailableError(EchoVaultError):
    status_code = 503
    code = ErrorCode.SERVICE_UNAVAILABLE
    message = "The service is temporarily unavailable."
