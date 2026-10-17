from typing import cast

from sqlalchemy import Table, UniqueConstraint

from echovault.config import get_settings
from echovault.db.models import (
    Base,
    IngestionJob,
    Memory,
    MemoryRevision,
    Project,
    ProjectMembership,
    Transcript,
    User,
)


def test_models_schema_and_tables_exist() -> None:
    settings = get_settings()
    assert Base.metadata.schema == settings.db_schema

    expected_tables = {
        "users",
        "projects",
        "project_memberships",
        "memories",
        "memory_revisions",
        "transcripts",
        "ingestion_jobs",
    }
    table_names = {t.name for t in Base.metadata.tables.values()}
    assert expected_tables.issubset(table_names)


def test_user_model_columns() -> None:
    table = cast(Table, User.__table__)
    cols = {c.name for c in table.columns}
    assert {"id", "email", "display_name", "created_at", "updated_at"}.issubset(cols)
    assert [c.name for c in table.primary_key.columns] == ["id"]


def test_project_model_columns_and_foreign_keys() -> None:
    table = cast(Table, Project.__table__)
    cols = {c.name for c in table.columns}
    assert {"id", "name", "description", "owner_id", "created_at", "updated_at"}.issubset(cols)
    assert [c.name for c in table.primary_key.columns] == ["id"]
    fk_targets = [fk.target_fullname for fk in table.foreign_keys]
    assert any("users.id" in target for target in fk_targets)


def test_project_membership_constraints() -> None:
    table = cast(Table, ProjectMembership.__table__)
    cols = {c.name for c in table.columns}
    assert {"id", "project_id", "user_id", "role", "created_at", "updated_at"}.issubset(cols)
    # Verify unique constraint on (project_id, user_id)
    unique_constraints = [
        [col.name for col in uq.columns]
        for uq in table.constraints
        if isinstance(uq, UniqueConstraint) and len(uq.columns) == 2
    ]
    assert ["project_id", "user_id"] in unique_constraints


def test_memory_model_constraints_and_indexes() -> None:
    table = cast(Table, Memory.__table__)
    cols = {c.name for c in table.columns}
    assert {
        "id",
        "project_id",
        "topic",
        "description",
        "tags",
        "content",
        "version",
        "source",
        "created_at",
        "updated_at",
    }.issubset(cols)

    # Unique constraint on (project_id, topic)
    unique_col_sets = [
        set(col.name for col in uq.columns)
        for uq in table.constraints
        if isinstance(uq, UniqueConstraint)
    ]
    assert {"project_id", "topic"} in unique_col_sets

    # Index on (project_id, updated_at)
    index_col_sets = [set(col.name for col in idx.columns) for idx in table.indexes]
    assert {"project_id", "updated_at"} in index_col_sets


def test_memory_revision_constraints() -> None:
    table = cast(Table, MemoryRevision.__table__)
    cols = {c.name for c in table.columns}
    assert {
        "id",
        "memory_id",
        "project_id",
        "version",
        "topic",
        "description",
        "tags",
        "content",
        "source",
        "metadata",
        "created_at",
    }.issubset(cols)

    unique_col_sets = [
        set(col.name for col in uq.columns)
        for uq in table.constraints
        if isinstance(uq, UniqueConstraint)
    ]
    assert {"memory_id", "version"} in unique_col_sets


def test_transcript_model_constraints() -> None:
    table = cast(Table, Transcript.__table__)
    cols = {c.name for c in table.columns}
    assert {
        "id",
        "project_id",
        "external_id",
        "source",
        "captured_at",
        "messages",
        "created_at",
    }.issubset(cols)

    unique_col_sets = [
        set(col.name for col in uq.columns)
        for uq in table.constraints
        if isinstance(uq, UniqueConstraint)
    ]
    assert {"project_id", "external_id"} in unique_col_sets


def test_ingestion_job_model_columns() -> None:
    table = cast(Table, IngestionJob.__table__)
    cols = {c.name for c in table.columns}
    assert {
        "id",
        "project_id",
        "transcript_id",
        "status",
        "retry_count",
        "error_details",
        "stats",
        "created_at",
        "updated_at",
    }.issubset(cols)
