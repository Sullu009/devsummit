import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from eventsphere_common.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SimulatedEmail(Base):
    """
    Local dev stand-in for a real email provider. Every 'email' is
    persisted here (and logged) instead of actually being sent, so the
    system is fully runnable without SMTP credentials. Swap this module
    for a real provider (SES/Postmark/etc.) in production.
    """
    __tablename__ = "simulated_emails"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    to_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProcessedEvent(Base):
    """Ensures at-least-once RabbitMQ delivery never creates duplicate notifications."""

    __tablename__ = "processed_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
