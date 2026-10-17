from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from echovault.config import Settings

logger = structlog.get_logger(__name__)


def _classify_db_error(error_str: str) -> str:
    """Classify a database error into a clear, non-leaking diagnostic message."""
    err_lower = error_str.lower()
    if "password authentication failed" in err_lower or "authentication failed" in err_lower:
        return "authentication failed"
    if "connection refused" in err_lower:
        return "connection refused: database server is unreachable"
    if "does not exist" in err_lower and "database" in err_lower:
        return "configured database does not exist"
    if "timeout" in err_lower or "timed out" in err_lower:
        return "connection timed out"
    if "name or service not known" in err_lower or "nodename nor servname provided" in err_lower:
        return "dns resolution failed: host unreachable"
    if "ssl" in err_lower:
        return "ssl connection negotiation failed"
    return f"database error: {error_str.splitlines()[0]}"


async def check_database_connection(settings: Settings) -> tuple[bool, str]:
    """Check whether the database is accessible and reports clear failure status.

    Returns:
        (is_ok, description)
    """
    if not settings.database_url:
        if settings.is_production:
            return False, "database_url is not configured"
        return True, "unconfigured (skipped in non-production)"

    target_url = settings.async_database_url
    if not target_url:
        return False, "database_url is invalid or missing async driver"

    engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if target_url.startswith("sqlite"):
        engine_kwargs["execution_options"] = {"schema_translate_map": {settings.db_schema: None}}
    else:
        engine_kwargs["connect_args"] = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }

    try:
        engine = create_async_engine(target_url, **engine_kwargs)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True, "ok"
        finally:
            await engine.dispose()
    except Exception as e:
        error_msg = str(e)
        diagnostic = _classify_db_error(error_msg)
        logger.warning("Database readiness check failed", error=error_msg, diagnostic=diagnostic)
        return False, diagnostic
