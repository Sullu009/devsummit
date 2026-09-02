import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from eventsphere_common.db import Base


class PaymentStatus(str, enum.Enum):
    CREATED = "CREATED"          # Razorpay order created, awaiting checkout
    SUCCEEDED = "SUCCEEDED"      # signature verified, booking confirmed
    FAILED = "FAILED"            # checkout failed or signature invalid
    REFUNDED = "REFUNDED"


def _uuid() -> str:
    return str(uuid.uuid4())


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), index=True, unique=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    organizer_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    event_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    razorpay_order_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    razorpay_signature: Mapped[str | None] = mapped_column(String(256), nullable=True)

    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus, name="payment_status"), nullable=False, default=PaymentStatus.CREATED)
    failure_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
