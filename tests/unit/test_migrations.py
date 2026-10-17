from pathlib import Path
from unittest.mock import patch

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from sqlalchemy.engine import create_engine

from echovault.config import Settings


def test_alembic_migrations_upgrade_and_downgrade(tmp_path: Path) -> None:
    db_file = tmp_path / "test_migration.db"
    db_url = f"sqlite:///{db_file}"

    test_settings = Settings(
        app_env="testing",
        database_url=db_url,
        db_schema="echovault",
    )

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", test_settings.async_database_url)

    with (
        patch("echovault.config.get_settings", return_value=test_settings),
        patch("echovault.db.base.get_settings", return_value=test_settings),
    ):
        # 1. Apply upgrade to head
        command.upgrade(alembic_cfg, "head")

        # 2. Inspect created tables in database
        sync_engine = create_engine(db_url)
        inspector = inspect(sync_engine)
        tables = set(inspector.get_table_names())

        expected_tables = {
            "alembic_version",
            "users",
            "projects",
            "project_memberships",
            "memories",
            "memory_revisions",
            "transcripts",
            "ingestion_jobs",
        }
        assert expected_tables.issubset(tables)

        # Verify columns on memories table
        memory_cols = {col["name"] for col in inspector.get_columns("memories")}
        assert {"id", "project_id", "topic", "content", "version"}.issubset(memory_cols)

        # 3. Apply downgrade to base
        command.downgrade(alembic_cfg, "base")

        # Verify tables are dropped
        sync_engine.dispose()
        fresh_engine = create_engine(db_url)
        fresh_inspector = inspect(fresh_engine)
        tables_after_downgrade = set(fresh_inspector.get_table_names())
        fresh_engine.dispose()
        assert not {"memories", "projects", "users"}.intersection(tables_after_downgrade)
