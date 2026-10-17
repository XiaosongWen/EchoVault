import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from echovault.core.context import get_request_id
from echovault.core.exceptions import EchoVaultError, ErrorCode

logger = structlog.get_logger(__name__)

STATUS_CODE_TO_ERROR_CODE: dict[int, ErrorCode] = {
    400: ErrorCode.INVALID_REQUEST,
    401: ErrorCode.UNAUTHORIZED,
    403: ErrorCode.PROJECT_ACCESS_DENIED,
    404: ErrorCode.RESOURCE_NOT_FOUND,
    409: ErrorCode.VERSION_CONFLICT,
    413: ErrorCode.PAYLOAD_TOO_LARGE,
    422: ErrorCode.VALIDATION_ERROR,
    429: ErrorCode.RATE_LIMITED,
    500: ErrorCode.INTERNAL_ERROR,
    503: ErrorCode.SERVICE_UNAVAILABLE,
}


def make_error_response(status_code: int, code: str, message: str, request_id: str) -> JSONResponse:
    content = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"X-Request-ID": request_id},
    )


def _get_req_id(request: Request) -> str:
    req_id: str = getattr(request.state, "request_id", "")
    return req_id or get_request_id()


async def echovault_error_handler(request: Request, exc: EchoVaultError) -> JSONResponse:
    request_id = _get_req_id(request)
    if exc.status_code >= 500:
        logger.error(
            "Server error occurred",
            error_code=str(exc.code),
            message=exc.message,
            request_id=request_id,
        )
    else:
        logger.warning(
            "Client error occurred",
            error_code=str(exc.code),
            message=exc.message,
            request_id=request_id,
        )
    return make_error_response(
        status_code=exc.status_code,
        code=str(exc.code),
        message=exc.message,
        request_id=request_id,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    request_id = _get_req_id(request)
    code = STATUS_CODE_TO_ERROR_CODE.get(
        exc.status_code,
        ErrorCode.INTERNAL_ERROR if exc.status_code >= 500 else ErrorCode.INVALID_REQUEST,
    )
    message = str(exc.detail) if exc.detail else "An HTTP error occurred."
    return make_error_response(
        status_code=exc.status_code,
        code=str(code),
        message=message,
        request_id=request_id,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _get_req_id(request)
    errors = exc.errors()
    if errors:
        first = errors[0]
        loc = ".".join(str(item) for item in first.get("loc", []) if item != "body")
        msg = first.get("msg", "Invalid value")
        message = f"Validation failed at '{loc}': {msg}" if loc else f"Validation failed: {msg}"
    else:
        message = "Validation failed for request parameters."

    return make_error_response(
        status_code=422,
        code=str(ErrorCode.VALIDATION_ERROR),
        message=message,
        request_id=request_id,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = _get_req_id(request)
    logger.exception(
        "Unhandled internal exception",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
    )
    return make_error_response(
        status_code=500,
        code=str(ErrorCode.INTERNAL_ERROR),
        message="An unexpected internal server error occurred.",
        request_id=request_id,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EchoVaultError, echovault_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
