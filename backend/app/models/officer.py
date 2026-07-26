"""Officer model."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Boolean, Date, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Officer(Base):
    __tablename__ = "officer"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    badge_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    rank: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(200), nullable=False)
    station: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    date_of_joining: Mapped[date | None] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    reported_firs = relationship(
        "FIR", foreign_keys="FIR.reporting_officer_id", back_populates="reporting_officer"
    )
    investigating_firs = relationship(
        "FIR", foreign_keys="FIR.investigating_officer_id", back_populates="investigating_officer"
    )
    investigations = relationship("Investigation", back_populates="officer")
    evidence_collected = relationship("Evidence", back_populates="collected_by_officer")
