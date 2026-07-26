"""Accused model."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Accused(Base):
    __tablename__ = "accused"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fir_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fir.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    alias: Mapped[str | None] = mapped_column(String(200))
    age: Mapped[int | None] = mapped_column(Integer)
    gender: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(20))
    id_type: Mapped[str | None] = mapped_column(String(50))
    id_number: Mapped[str | None] = mapped_column(String(100))
    occupation: Mapped[str | None] = mapped_column(String(200))
    is_arrested: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    arrest_date: Mapped[date | None] = mapped_column(Date)
    bail_status: Mapped[str] = mapped_column(
        String(50), default="not_applicable"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    fir = relationship("FIR", back_populates="accused_list")
    criminal_history = relationship(
        "CriminalHistory", back_populates="accused", cascade="all, delete-orphan"
    )
    financial_transactions = relationship(
        "FinancialTransaction", back_populates="accused"
    )
    location_records = relationship(
        "LocationHistory", back_populates="accused", cascade="all, delete-orphan"
    )
