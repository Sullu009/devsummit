import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eventsphere_common.db import Base


class BookingStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"


def _uuid() -> str:
    return str(uuid.uuid4())


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    reservation_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    event_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    organizer_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(Enum(BookingStatus, name="booking_status"), nullable=False, default=BookingStatus.PENDING_PAYMENT)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items: Mapped[list["BookingItem"]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class BookingItem(Base):
    __tablename__ = "booking_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    booking_id: Mapped[str] = mapped_column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), index=True, nullable=False)
    ticket_type_id: Mapped[str] = mapped_column(String(36), nullable=False)
    ticket_type_name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    booking: Mapped[Booking] = relationship(back_populates="items")


class IdempotentRequest(Base):
    """Guards booking mutations (reserve/confirm/cancel) against duplicate client retries."""

    __tablename__ = "idempotent_requests"

    idempotency_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    booking_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
