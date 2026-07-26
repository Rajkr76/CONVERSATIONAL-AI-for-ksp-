"""Financial transaction model."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import String, Text, Boolean, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class FinancialTransaction(Base):
    __tablename__ = "financial_transaction"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fir_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fir.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    accused_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accused.id", ondelete="SET NULL"),
        index=True,
    )
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    from_account: Mapped[str | None] = mapped_column(String(100))
    to_account: Mapped[str | None] = mapped_column(String(100))
    bank_name: Mapped[str | None] = mapped_column(String(200))
    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    is_suspicious: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True
    )
    remarks: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    fir = relationship("FIR", back_populates="financial_transactions")
    accused = relationship("Accused", back_populates="financial_transactions")
