from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from echovault.db.base import Base, JSONType

if TYPE_CHECKING:
    from echovault.db.models.projects import Project
    from echovault.db.models.transcripts import Transcript


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    __table_args__ = (Index("idx_ingestion_jobs_project_status", "project_id", "status"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    transcript_id: Mapped[str] = mapped_column(
        ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    project: Mapped["Project"] = relationship("Project", back_populates="ingestion_jobs")
    transcript: Mapped["Transcript"] = relationship("Transcript", back_populates="ingestion_jobs")
