from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from echovault.db.base import Base, JSONType

if TYPE_CHECKING:
    from echovault.db.models.memory_revisions import MemoryRevision
    from echovault.db.models.projects import Project


class Memory(Base):
    __tablename__ = "memories"
    __table_args__ = (
        UniqueConstraint("project_id", "topic", name="uq_memories_project_topic"),
        Index("idx_memories_project_updated", "project_id", "updated_at"),
        Index("idx_memories_project_topic", "project_id", "topic"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[Any]] = mapped_column(JSONType, nullable=False, default=list)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source: Mapped[str] = mapped_column(String(64), nullable=False, default="manual")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="memories")
    revisions: Mapped[list["MemoryRevision"]] = relationship(
        "MemoryRevision", back_populates="memory", cascade="all, delete-orphan"
    )
