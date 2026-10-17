import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from echovault.config import Settings
from echovault.core.context import get_request_id

SENSITIVE_KEYS = {
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "jwt",
    "access_token",
    "refresh_token",
    "service_role_key",
    "private_key",
}


def _redact_value(val: Any) -> Any:
    if isinstance(val, dict):
        return {
            k: ("[REDACTED]" if any(s in k.lower() for s in SENSITIVE_KEYS) else _redact_value(v))
            for k, v in val.items()
        }
    if isinstance(val, list):
        return [_redact_value(item) for item in val]
    return val


def redact_sensitive_data(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Mask sensitive values in log event dict."""
    for key, value in list(event_dict.items()):
        key_lower = key.lower()
        if any(sensitive in key_lower for sensitive in SENSITIVE_KEYS):
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, (dict, list)):
            event_dict[key] = _redact_value(value)
    return event_dict


def add_request_id(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """Inject request_id into log event if available."""
    if "request_id" not in event_dict:
        req_id = get_request_id()
        if req_id:
            event_dict["request_id"] = req_id
    return event_dict


def setup_logging(settings: Settings) -> None:
    """Configure structured logging for the application."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    use_json = settings.log_format == "json" or (
        settings.log_format == "auto" and settings.is_production
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        add_request_id,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        redact_sensitive_data,
        structlog.processors.StackInfoRenderer(),
    ]

    if use_json:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())

    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)

    for name in ("uvicorn.access", "uvicorn.error"):
        u_logger = logging.getLogger(name)
        u_logger.handlers = [handler]
        u_logger.propagate = False
