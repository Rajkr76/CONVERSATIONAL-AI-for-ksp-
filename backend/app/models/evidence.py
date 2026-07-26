"""Evidence model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fir_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fir.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    evidence_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    collected_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("officer.id", ondelete="SET NULL")
    )
    collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    storage_location: Mapped[str | None] = mapped_column(String(200))
    chain_of_custody: Mapped[str | None] = mapped_column(Text)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    fir = relationship("FIR", back_populates="evidence_items")
    collected_by_officer = relationship("Officer", back_populates="evidence_collected")
