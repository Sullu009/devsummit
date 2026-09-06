import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eventsphere_common.db import Base


class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    CANCELLED = "CANCELLED"


class EventCategory(str, enum.Enum):
    MUSIC = "MUSIC"
    TECH = "TECH"
    BUSINESS = "BUSINESS"
    ARTS = "ARTS"
    SPORTS = "SPORTS"
    FOOD = "FOOD"
    COMMUNITY = "COMMUNITY"
    OTHER = "OTHER"


def _uuid() -> str:
    return str(uuid.uuid4())


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    organizer_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(280), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    category: Mapped[EventCategory] = mapped_column(Enum(EventCategory, name="event_category"), nullable=False, default=EventCategory.OTHER)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus, name="event_status"), nullable=False, default=EventStatus.DRAFT)
    cover_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    venue_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    venue_address: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False, default="")

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ticket_types: Mapped[list["TicketType"]] = relationship(back_populates="event", cascade="all, delete-orphan", order_by="TicketType.price")
    tracks: Mapped[list["Track"]] = relationship(back_populates="event", cascade="all, delete-orphan", order_by="Track.order")
    speakers: Mapped[list["Speaker"]] = relationship(back_populates="event", cascade="all, delete-orphan", order_by="Speaker.name")
    sessions: Mapped[list["Session"]] = relationship(back_populates="event", cascade="all, delete-orphan", order_by="Session.start_time")


class TicketType(Base):
    __tablename__ = "ticket_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity_total: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False)
    sale_starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sale_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    event: Mapped[Event] = relationship(back_populates="ticket_types")


class AvailabilityAdjustment(Base):
    """Idempotency ledger so a retried booking-service call never double-decrements stock."""

    __tablename__ = "availability_adjustments"

    idempotency_key: Mapped[str] = mapped_column(String(120), primary_key=True)
    ticket_type_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    room_location: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    color_code: Mapped[str] = mapped_column(String(30), nullable=False, default="#6366F1")
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    event: Mapped[Event] = relationship(back_populates="tracks")
    sessions: Mapped[list["Session"]] = relationship(back_populates="track", cascade="all, delete-orphan")


class Speaker(Base):
    __tablename__ = "speakers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role_title: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    company: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    bio: Mapped[str] = mapped_column(Text, nullable=False, default="")
    avatar_url: Mapped[str] = mapped_column(String(1024), nullable=False, default="")
    github_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    twitter_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    event: Mapped[Event] = relationship(back_populates="speakers")
    sessions: Mapped[list["Session"]] = relationship(back_populates="speaker")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id", ondelete="CASCADE"), index=True, nullable=False)
    track_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("tracks.id", ondelete="SET NULL"), index=True, nullable=True)
    speaker_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("speakers.id", ondelete="SET NULL"), index=True, nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    abstract: Mapped[str] = mapped_column(Text, nullable=False, default="")
    session_type: Mapped[str] = mapped_column(String(50), nullable=False, default="TALK")  # KEYNOTE, TALK, WORKSHOP, PANEL
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    slides_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    event: Mapped[Event] = relationship(back_populates="sessions")
    track: Mapped[Track | None] = relationship(back_populates="sessions")
    speaker: Mapped[Speaker | None] = relationship(back_populates="sessions")
