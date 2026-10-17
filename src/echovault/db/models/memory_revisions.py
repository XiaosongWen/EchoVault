from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from echovault.db.base import Base, JSONType

if TYPE_CHECKING:
    from echovault.db.models.memories import Memory
    from echovault.db.models.projects import Project


class MemoryRevision(Base):
    __tablename__ = "memory_revisions"
    __table_args__ = (
        UniqueConstraint("memory_id", "version", name="uq_memory_revisions_memory_version"),
        Index("idx_memory_revisions_project_id", "project_id"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    memory_id: Mapped[str] = mapped_column(
        ForeignKey("memories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[Any]] = mapped_column(JSONType, nullable=False, default=list)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    # Maps column name 'metadata' while avoiding conflict with SQLAlchemy's Base.metadata
    revision_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONType, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    memory: Mapped["Memory"] = relationship("Memory", back_populates="revisions")
    project: Mapped["Project"] = relationship("Project")
