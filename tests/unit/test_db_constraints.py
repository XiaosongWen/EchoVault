from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from echovault.config import get_settings
from echovault.db.models import (
    Base,
    Memory,
    MemoryRevision,
    Project,
    ProjectMembership,
    Transcript,
    User,
)


@pytest.fixture
async def async_db() -> AsyncIterator[AsyncSession]:
    settings = get_settings()
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        execution_options={"schema_translate_map": {settings.db_schema: None}},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_memory_unique_topic_within_project(async_db: AsyncSession) -> None:
    """Verify unique constraint on (project_id, topic).

    Duplicate topics in the same project must be rejected.
    Identical topics across different projects must be allowed.
    """
    # 1. Create a user and two projects
    user = User(id="usr_001", email="test@example.com", display_name="Test User")
    proj_a = Project(id="proj_a", name="Project A", owner_id=user.id)
    proj_b = Project(id="proj_b", name="Project B", owner_id=user.id)
    async_db.add_all([user, proj_a, proj_b])
    await async_db.commit()

    # 2. Add memory to Project A with topic "auth-flow"
    mem_a1 = Memory(
        id="mem_001",
        project_id="proj_a",
        topic="auth-flow",
        description="Auth flow in Project A",
        content="# Auth Flow",
        version=1,
    )
    async_db.add(mem_a1)
    await async_db.commit()

    # 3. Add memory to Project B with the SAME topic "auth-flow" -> MUST SUCCEED
    mem_b1 = Memory(
        id="mem_002",
        project_id="proj_b",
        topic="auth-flow",
        description="Auth flow in Project B",
        content="# Auth Flow B",
        version=1,
    )
    async_db.add(mem_b1)
    await async_db.commit()

    # 4. Attempt to add duplicate topic "auth-flow" to Project A -> MUST FAIL
    mem_a2 = Memory(
        id="mem_003",
        project_id="proj_a",
        topic="auth-flow",
        description="Duplicate auth flow in Project A",
        content="# Auth Flow Duplicate",
        version=1,
    )
    async_db.add(mem_a2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
    await async_db.rollback()


@pytest.mark.asyncio
async def test_project_membership_unique_constraint(async_db: AsyncSession) -> None:
    user = User(id="usr_002", email="collab@example.com")
    proj = Project(id="proj_c", name="Project C", owner_id=user.id)
    async_db.add_all([user, proj])
    await async_db.commit()

    pm1 = ProjectMembership(id="pm_001", project_id=proj.id, user_id=user.id, role="owner")
    async_db.add(pm1)
    await async_db.commit()

    # Duplicate membership for same (project_id, user_id) must be rejected
    pm2 = ProjectMembership(id="pm_002", project_id=proj.id, user_id=user.id, role="member")
    async_db.add(pm2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
    await async_db.rollback()


@pytest.mark.asyncio
async def test_transcript_idempotency_constraint(async_db: AsyncSession) -> None:
    user = User(id="usr_003", email="ingest@example.com")
    proj = Project(id="proj_d", name="Project D", owner_id=user.id)
    async_db.add_all([user, proj])
    await async_db.commit()

    now = datetime.now(UTC)
    tr1 = Transcript(
        id="tr_001",
        project_id=proj.id,
        external_id="session_xyz",
        source="claude-code",
        captured_at=now,
        messages=[{"role": "user", "content": "hello"}],
    )
    async_db.add(tr1)
    await async_db.commit()

    # Repeating with identical external_id in the same project must violate uniqueness
    tr2 = Transcript(
        id="tr_002",
        project_id=proj.id,
        external_id="session_xyz",
        source="claude-code",
        captured_at=now,
        messages=[{"role": "user", "content": "hello again"}],
    )
    async_db.add(tr2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
    await async_db.rollback()


@pytest.mark.asyncio
async def test_memory_revision_version_constraint(async_db: AsyncSession) -> None:
    user = User(id="usr_004", email="rev@example.com")
    proj = Project(id="proj_e", name="Project E", owner_id=user.id)
    mem = Memory(
        id="mem_010",
        project_id=proj.id,
        topic="cache-layer",
        description="",
        content="# Cache",
        version=1,
    )
    async_db.add_all([user, proj, mem])
    await async_db.commit()

    rev1 = MemoryRevision(
        id="rev_001",
        memory_id=mem.id,
        project_id=proj.id,
        version=1,
        topic=mem.topic,
        content=mem.content,
        source="manual",
    )
    async_db.add(rev1)
    await async_db.commit()

    # Duplicate version for same memory_id must be rejected
    rev2 = MemoryRevision(
        id="rev_002",
        memory_id=mem.id,
        project_id=proj.id,
        version=1,
        topic=mem.topic,
        content="different content",
        source="manual",
    )
    async_db.add(rev2)
    with pytest.raises(IntegrityError):
        await async_db.commit()
    await async_db.rollback()
