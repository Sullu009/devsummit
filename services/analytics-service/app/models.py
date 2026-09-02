from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from eventsphere_common.db import Base


class EventStats(Base):
    """
    A single running-aggregate row per event, updated incrementally as
    domain events arrive. This is intentionally denormalized (vs. the
    normalized source-of-truth tables in event/booking/payment-service)
    because analytics reads are dashboard-latency-sensitive and this
    service's job is exactly to pre-aggregate for fast reads.
    """
    __tablename__ = "event_stats"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    organizer_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False, default="")

    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bookings_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bookings_confirmed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bookings_cancelled: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tickets_sold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    refunds_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    refunds_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    attendance_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
