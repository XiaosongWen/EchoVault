import uuid
from contextvars import ContextVar

_request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="")


def generate_request_id() -> str:
    """Generate a unique request identifier with 'req_' prefix."""
    return f"req_{uuid.uuid4().hex[:12]}"


def get_request_id() -> str:
    """Retrieve current request ID from context or generate one if missing."""
    req_id = _request_id_ctx_var.get()
    if not req_id:
        req_id = generate_request_id()
        _request_id_ctx_var.set(req_id)
    return req_id


def set_request_id(req_id: str) -> None:
    """Set request ID for current context."""
    _request_id_ctx_var.set(req_id)
