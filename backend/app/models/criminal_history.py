"""Criminal history model."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Text, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CriminalHistory(Base):
    __tablename__ = "criminal_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    accused_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accused.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    offense_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    case_number: Mapped[str | None] = mapped_column(String(50))
    court_name: Mapped[str | None] = mapped_column(String(200))
    conviction_date: Mapped[date | None] = mapped_column(Date)
    sentence: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50), default="recorded")
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    accused = relationship("Accused", back_populates="criminal_history")
