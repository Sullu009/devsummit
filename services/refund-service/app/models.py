import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from eventsphere_common.db import Base


class RefundStatus(str, enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


def _uuid() -> str:
    return str(uuid.uuid4())


class Refund(Base):
    __tablename__ = "refunds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    payment_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False, default="Attendee-requested cancellation")
    status: Mapped[RefundStatus] = mapped_column(Enum(RefundStatus, name="refund_status"), nullable=False, default=RefundStatus.PENDING)
    razorpay_refund_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
