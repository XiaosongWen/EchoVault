"""Initial schema for EchoVault.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-10-17 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from echovault.config import get_settings

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _get_schema() -> str | None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        return None
    return get_settings().db_schema


def upgrade() -> None:
    schema = _get_schema()
    json_type = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")

    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False, schema=schema)

    # 2. projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_id", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            [f"{schema}.users.id" if schema else "users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index("ix_projects_owner_id", "projects", ["owner_id"], unique=False, schema=schema)

    # 3. project_memberships
    op.create_table(
        "project_memberships",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="member"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{schema}.projects.id" if schema else "projects.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{schema}.users.id" if schema else "users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_memberships_project_user"),
        schema=schema,
    )
    op.create_index(
        "ix_project_memberships_project_id",
        "project_memberships",
        ["project_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "ix_project_memberships_user_id",
        "project_memberships",
        ["user_id"],
        unique=False,
        schema=schema,
    )

    # 4. memories
    op.create_table(
        "memories",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", json_type, nullable=False, server_default="[]"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("source", sa.String(length=64), nullable=False, server_default="manual"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{schema}.projects.id" if schema else "projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "topic", name="uq_memories_project_topic"),
        schema=schema,
    )
    op.create_index(
        "ix_memories_project_id", "memories", ["project_id"], unique=False, schema=schema
    )
    op.create_index(
        "idx_memories_project_updated",
        "memories",
        ["project_id", "updated_at"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "idx_memories_project_topic",
        "memories",
        ["project_id", "topic"],
        unique=False,
        schema=schema,
    )

    # 5. memory_revisions
    op.create_table(
        "memory_revisions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("memory_id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", json_type, nullable=False, server_default="[]"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("metadata", json_type, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["memory_id"],
            [f"{schema}.memories.id" if schema else "memories.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{schema}.projects.id" if schema else "projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("memory_id", "version", name="uq_memory_revisions_memory_version"),
        schema=schema,
    )
    op.create_index(
        "ix_memory_revisions_memory_id",
        "memory_revisions",
        ["memory_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "idx_memory_revisions_project_id",
        "memory_revisions",
        ["project_id"],
        unique=False,
        schema=schema,
    )

    # 6. transcripts
    op.create_table(
        "transcripts",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("messages", json_type, nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{schema}.projects.id" if schema else "projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "external_id", name="uq_transcripts_project_external_id"),
        schema=schema,
    )
    op.create_index(
        "ix_transcripts_project_id",
        "transcripts",
        ["project_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "ix_transcripts_external_id",
        "transcripts",
        ["external_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "idx_transcripts_project_captured",
        "transcripts",
        ["project_id", "captured_at"],
        unique=False,
        schema=schema,
    )

    # 7. ingestion_jobs
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("project_id", sa.String(length=64), nullable=False),
        sa.Column("transcript_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_details", sa.Text(), nullable=True),
        sa.Column("stats", json_type, nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{schema}.projects.id" if schema else "projects.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["transcript_id"],
            [f"{schema}.transcripts.id" if schema else "transcripts.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema=schema,
    )
    op.create_index(
        "ix_ingestion_jobs_project_id",
        "ingestion_jobs",
        ["project_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "ix_ingestion_jobs_transcript_id",
        "ingestion_jobs",
        ["transcript_id"],
        unique=False,
        schema=schema,
    )
    op.create_index(
        "idx_ingestion_jobs_project_status",
        "ingestion_jobs",
        ["project_id", "status"],
        unique=False,
        schema=schema,
    )


def downgrade() -> None:
    schema = _get_schema()

    op.drop_table("ingestion_jobs", schema=schema)
    op.drop_table("transcripts", schema=schema)
    op.drop_table("memory_revisions", schema=schema)
    op.drop_table("memories", schema=schema)
    op.drop_table("project_memberships", schema=schema)
    op.drop_table("projects", schema=schema)
    op.drop_table("users", schema=schema)
