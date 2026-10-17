from pathlib import Path

import pytest

from echovault.config import Settings
from echovault.db.readiness import _classify_db_error, check_database_connection


def test_classify_db_error() -> None:
    msg1 = _classify_db_error("password authentication failed for user 'foo'")
    assert msg1 == "authentication failed"
    assert "unreachable" in _classify_db_error("Connection refused: [Errno 61]")
    msg2 = _classify_db_error("database 'unknown_db' does not exist")
    assert msg2 == "configured database does not exist"
    assert _classify_db_error("Connection timed out after 5000ms") == "connection timed out"
    msg3 = _classify_db_error("nodename nor servname provided, or not known")
    assert "dns resolution failed" in msg3


@pytest.mark.asyncio
async def test_readiness_unconfigured_in_dev_and_prod() -> None:
    dev_settings = Settings(app_env="development", database_url="")
    ok, msg = await check_database_connection(dev_settings)
    assert ok is True
    assert "unconfigured" in msg

    prod_settings = Settings(app_env="production", database_url="")
    ok, msg = await check_database_connection(prod_settings)
    assert ok is False
    assert "not configured" in msg


@pytest.mark.asyncio
async def test_readiness_success_with_sqlite(tmp_path: Path) -> None:
    db_file = tmp_path / "test_readiness.db"
    settings = Settings(
        app_env="development",
        database_url=f"sqlite:///{db_file}",
    )
    ok, msg = await check_database_connection(settings)
    assert ok is True
    assert msg == "ok"


@pytest.mark.asyncio
async def test_readiness_connection_failure_reported_clearly() -> None:
    # Pointing to an invalid localhost port where no database is running
    settings = Settings(
        app_env="development",
        database_url="postgresql://user:pass@127.0.0.1:54329/testdb",
    )
    ok, msg = await check_database_connection(settings)
    assert ok is False
    expected_terms = ["connection refused", "unreachable", "timed out", "error"]
    assert any(term in msg.lower() for term in expected_terms)
    # Ensure sensitive credentials are never leaked in the diagnostic message
    assert "pass" not in msg
    assert "user" not in msg
