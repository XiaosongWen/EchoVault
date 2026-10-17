import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from echovault.config import Settings

logger = structlog.get_logger(__name__)


async def check_database_connection(settings: Settings) -> tuple[bool, str]:
    """Check whether the database is accessible.

    Returns:
        (is_ok, description)
    """
    if not settings.database_url:
        if settings.is_production:
            return False, "database_url is not configured"
        return True, "unconfigured (skipped in non-production)"

    try:
        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True, "ok"
        finally:
            await engine.dispose()
    except Exception as e:
        logger.warning("Database readiness check failed", error=str(e))
        return False, "unavailable"
