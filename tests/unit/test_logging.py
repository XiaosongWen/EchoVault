from unittest.mock import MagicMock

from echovault.config import Settings
from echovault.core.context import set_request_id
from echovault.core.logging import add_request_id, redact_sensitive_data, setup_logging


def test_setup_logging_dev() -> None:
    settings = Settings(app_env="development", log_level="DEBUG")
    setup_logging(settings)


def test_setup_logging_prod() -> None:
    settings = Settings(app_env="production", log_level="INFO", log_format="json")
    setup_logging(settings)


def test_redact_sensitive_keys() -> None:
    dummy_logger = MagicMock()
    event_dict = {
        "event": "user login",
        "password": "plain_password_123",
        "api_key": "sk-1234567890",
        "nested": {
            "jwt_token": "token_abc",
            "safe_key": "safe_val",
        },
        "safe_field": "public_data",
    }
    redacted = redact_sensitive_data(dummy_logger, "info", event_dict)

    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["jwt_token"] == "[REDACTED]"
    assert redacted["nested"]["safe_key"] == "safe_val"
    assert redacted["safe_field"] == "public_data"


def test_add_request_id_processor() -> None:
    dummy_logger = MagicMock()
    set_request_id("req_sample_id")
    event_dict = {"event": "test"}
    processed = add_request_id(dummy_logger, "info", event_dict)
    assert processed["request_id"] == "req_sample_id"
