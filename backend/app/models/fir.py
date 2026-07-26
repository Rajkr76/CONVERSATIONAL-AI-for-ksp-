"""FIR (First Information Report) model."""

import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, Text, Date, DateTime, Float, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FIR(Base):
    __tablename__ = "fir"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fir_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    fir_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fir_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open", index=True
    )
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium", index=True
    )
    ipc_sections: Mapped[list | None] = mapped_column(ARRAY(Text))
    station: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    district: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(String(100), default="Karnataka")
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)

    # Foreign keys
    reporting_officer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("officer.id", ondelete="SET NULL")
    )
    investigating_officer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("officer.id", ondelete="SET NULL")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    reporting_officer = relationship(
        "Officer", foreign_keys=[reporting_officer_id], back_populates="reported_firs"
    )
    investigating_officer = relationship(
        "Officer", foreign_keys=[investigating_officer_id], back_populates="investigating_firs"
    )
    accused_list = relationship("Accused", back_populates="fir", cascade="all, delete-orphan")
    victims = relationship("Victim", back_populates="fir", cascade="all, delete-orphan")
    investigations = relationship("Investigation", back_populates="fir", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="fir", cascade="all, delete-orphan")
    witnesses = relationship("Witness", back_populates="fir", cascade="all, delete-orphan")
    financial_transactions = relationship("FinancialTransaction", back_populates="fir", cascade="all, delete-orphan")
    location_records = relationship("LocationHistory", back_populates="fir")
