"""
Canonical EventSphere domain event contracts.

Every event published to RabbitMQ uses this envelope so consumers can
deserialize generically and dispatch on `event_type`.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "EventViewed",
    "EventPublished",
    "EventCancelled",
    "EventUpdated",
    "BookingCreated",
    "BookingConfirmed",
    "BookingCancelled",
    "BookingExpired",
    "PaymentSucceeded",
    "PaymentFailed",
    "RefundRequested",
    "RefundProcessed",
    "NotificationCreated",
    "AttendanceRecorded",
]


class EventEnvelope(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_service: str
    data: dict[str, Any]

    def routing_key(self) -> str:
        return f"eventsphere.{self.event_type.lower()}"
