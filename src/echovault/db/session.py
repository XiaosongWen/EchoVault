from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from echovault.config import Settings, get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(settings: Settings | None = None) -> AsyncEngine:
    """Get or create the global AsyncEngine."""
    global _engine
    if _engine is not None:
        return _engine

    cfg = settings or get_settings()
    url = cfg.async_database_url
    if not url:
        raise ValueError("database_url is not configured")

    engine_kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
    }

    if url.startswith("sqlite"):
        # SQLite: translate the configured Postgres schema namespace to default
        engine_kwargs["execution_options"] = {"schema_translate_map": {cfg.db_schema: None}}
    else:
        # PostgreSQL / asyncpg: set search_path to the isolated schema
        engine_kwargs["pool_size"] = cfg.db_pool_size
        engine_kwargs["max_overflow"] = cfg.db_max_overflow
        engine_kwargs["pool_recycle"] = cfg.db_pool_recycle
        engine_kwargs["pool_timeout"] = cfg.db_pool_timeout
        engine_kwargs["connect_args"] = {
            "server_settings": {
                "search_path": f"{cfg.db_schema},public",
            },
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }

    _engine = create_async_engine(url, **engine_kwargs)
    return _engine


def get_session_factory(
    engine: AsyncEngine | None = None,
    settings: Settings | None = None,
) -> async_sessionmaker[AsyncSession]:
    """Get or create the global async session factory."""
    global _session_factory
    if _session_factory is not None and engine is None:
        return _session_factory

    eng = engine or get_engine(settings)
    _session_factory = async_sessionmaker(
        bind=eng,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    return _session_factory


async def close_engine() -> None:
    """Dispose of the engine connection pool (e.g., during app shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency for yielding an async database session per request."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
