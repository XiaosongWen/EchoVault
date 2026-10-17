import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from echovault.config import get_settings
from echovault.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = getattr(context, "config", None)

# Interpret the config file for Python logging.
if config is not None and config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_settings_obj():
    return get_settings()


def get_url() -> str:
    """Retrieve the asynchronous database URL from Alembic config or application settings."""
    cfg = context.config
    if cfg is not None:
        ini_url = cfg.get_main_option("sqlalchemy.url")
        if ini_url:
            return ini_url
    url = get_settings_obj().async_database_url
    if not url:
        raise ValueError("database_url is not configured in settings")
    return url


def include_object(
    object_: Any,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: Any,
) -> bool:
    """Filter schema objects to ensure only EchoVault tables are tracked.

    Tables in the public schema or other schemas belonging to other applications
    sharing the PostgreSQL instance will be completely ignored.
    """
    settings = get_settings_obj()
    if type_ == "table":
        if getattr(object_, "schema", None) != settings.db_schema:
            return False
    return True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    settings = get_settings_obj()
    url = get_url()
    schema = settings.db_schema
    is_sqlite = url.startswith("sqlite")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=None if is_sqlite else schema,
        version_table="alembic_version",
        include_schemas=not is_sqlite,
        include_object=include_object,
        render_as_batch=is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    settings = get_settings_obj()
    schema = settings.db_schema
    is_sqlite = connection.dialect.name == "sqlite"

    if not is_sqlite:
        # Guarantee that our dedicated schema exists before running migrations
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=None if is_sqlite else schema,
        version_table="alembic_version",
        include_schemas=not is_sqlite,
        include_object=include_object,
        render_as_batch=is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with an AsyncEngine."""
    cfg = context.config
    configuration = cfg.get_section(cfg.config_ini_section) or {}
    url = get_url()
    configuration["sqlalchemy.url"] = url

    connect_args: dict[str, Any] = {}
    if not url.startswith("sqlite"):
        # Supabase PgBouncer pooler (port 6543) compatibility
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await connection.commit()

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
