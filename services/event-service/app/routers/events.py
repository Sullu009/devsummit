import re
import uuid
from datetime import datetime, timezone

from eventsphere_common.auth_deps import CurrentUser, get_optional_user, require_roles
from eventsphere_common.bus import publish_event
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..database import get_db
from ..models import Event, EventCategory, EventStatus, Session as SessionModel, Speaker, TicketType, Track
from ..schemas import (
    EventCreate,
    EventOut,
    EventSummaryOut,
    EventUpdate,
    FullScheduleOut,
    PaginatedEvents,
    ScheduleDay,
    ScheduleSlot,
    SessionCreate,
    SessionOut,
    SpeakerCreate,
    SpeakerOut,
    SpeakerWithSessionsOut,
    TrackCreate,
    TrackOut,
)

router = APIRouter(prefix="/events", tags=["events"])


def _slugify(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{base}-{uuid.uuid4().hex[:6]}"


def _publish_safe(event_type: str, data: dict) -> None:
    try:
        publish_event(event_type, settings.service_name, data)
    except Exception:  # noqa: BLE001
        # Event publishing must never fail the primary request in this demo-scale system.
        pass


@router.post("", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = Event(
        organizer_id=user.id,
        title=payload.title,
        slug=_slugify(payload.title),
        description=payload.description,
        category=payload.category,
        status=EventStatus.DRAFT,
        cover_image_url=payload.cover_image_url,
        venue_name=payload.venue_name,
        venue_address=payload.venue_address,
        city=payload.city,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
    )
    for tt in payload.ticket_types:
        event.ticket_types.append(
            TicketType(
                name=tt.name,
                description=tt.description,
                price=tt.price,
                quantity_total=tt.quantity_total,
                quantity_available=tt.quantity_total,
                sale_starts_at=tt.sale_starts_at,
                sale_ends_at=tt.sale_ends_at,
            )
        )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=PaginatedEvents)
def list_events(
    q: str | None = None,
    category: EventCategory | None = None,
    city: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mine: bool = False,
    admin_all: bool = False,
    db: Session = Depends(get_db),
    user: CurrentUser | None = Depends(get_optional_user),
):
    stmt = select(Event).options(selectinload(Event.ticket_types))

    if admin_all:
        if not user or user.role != "ADMIN":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
        # no status filter - admins moderate events in any state
    elif mine:
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Login required to view your events")
        stmt = stmt.where(Event.organizer_id == user.id)
    else:
        stmt = stmt.where(Event.status == EventStatus.PUBLISHED)

    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(or_(func.lower(Event.title).like(like), func.lower(Event.description).like(like), func.lower(Event.city).like(like)))
    if category:
        stmt = stmt.where(Event.category == category)
    if city:
        stmt = stmt.where(func.lower(Event.city) == city.lower())
    if date_from:
        stmt = stmt.where(Event.starts_at >= date_from)
    if date_to:
        stmt = stmt.where(Event.starts_at <= date_to)

    stmt = stmt.order_by(Event.starts_at.asc())

    all_events = db.execute(stmt).scalars().unique().all()

    summaries = []
    for e in all_events:
        prices = [float(t.price) for t in e.ticket_types] or [0]
        lo, hi = min(prices), max(prices)
        if min_price is not None and hi < min_price:
            continue
        if max_price is not None and lo > max_price:
            continue
        summaries.append(
            EventSummaryOut(
                id=e.id, organizer_id=e.organizer_id, title=e.title, slug=e.slug, category=e.category,
                status=e.status, cover_image_url=e.cover_image_url, city=e.city, starts_at=e.starts_at,
                min_price=lo, max_price=hi,
            )
        )

    total = len(summaries)
    start = (page - 1) * page_size
    page_items = summaries[start:start + page_size]
    return PaginatedEvents(items=page_items, total=total, page=page, page_size=page_size)


def _get_owned_event(event_id: str, user: CurrentUser, db: Session) -> Event:
    event = db.get(
        Event,
        event_id,
        options=[
            selectinload(Event.ticket_types),
            selectinload(Event.tracks),
            selectinload(Event.speakers),
            selectinload(Event.sessions).selectinload(SessionModel.track),
            selectinload(Event.sessions).selectinload(SessionModel.speaker),
        ],
    )
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    if event.organizer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not own this event")
    return event


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db), user: CurrentUser | None = Depends(get_optional_user)):
    event = db.get(
        Event,
        event_id,
        options=[
            selectinload(Event.ticket_types),
            selectinload(Event.tracks),
            selectinload(Event.speakers),
            selectinload(Event.sessions).selectinload(SessionModel.track),
            selectinload(Event.sessions).selectinload(SessionModel.speaker),
        ],
    )
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    is_owner = user and (user.id == event.organizer_id or user.role == "ADMIN")
    if event.status != EventStatus.PUBLISHED and not is_owner:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

    _publish_safe("EventViewed", {"event_id": event.id, "viewer_id": user.id if user else None})
    return event


@router.patch("/{event_id}", response_model=EventOut)
def update_event(event_id: str, payload: EventUpdate, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cancelled events cannot be edited")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    _publish_safe("EventUpdated", {"event_id": event.id})
    return event


@router.post("/{event_id}/ticket-types", response_model=EventOut)
def add_ticket_type(event_id: str, payload: dict, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    from ..schemas import TicketTypeCreate

    tt_payload = TicketTypeCreate.model_validate(payload)
    event = _get_owned_event(event_id, user, db)
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cancelled events cannot be edited")
    event.ticket_types.append(
        TicketType(
            name=tt_payload.name, description=tt_payload.description, price=tt_payload.price,
            quantity_total=tt_payload.quantity_total, quantity_available=tt_payload.quantity_total,
            sale_starts_at=tt_payload.sale_starts_at, sale_ends_at=tt_payload.sale_ends_at,
        )
    )
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/publish", response_model=EventOut)
def publish_event_endpoint(event_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    if event.status != EventStatus.DRAFT:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot publish an event in status {event.status.value}")
    if not event.ticket_types:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Add at least one ticket type before publishing")

    event.status = EventStatus.PUBLISHED
    db.commit()
    db.refresh(event)
    _publish_safe("EventPublished", {"event_id": event.id, "organizer_id": event.organizer_id, "title": event.title})
    return event


@router.post("/{event_id}/cancel", response_model=EventOut)
def cancel_event(event_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    if event.status == EventStatus.CANCELLED:
        raise HTTPException(status.HTTP_409_CONFLICT, "Event is already cancelled")

    event.status = EventStatus.CANCELLED
    db.commit()
    db.refresh(event)
    _publish_safe("EventCancelled", {"event_id": event.id, "organizer_id": event.organizer_id, "title": event.title})
    return event


# --- DevSummit Conference Extensions: Tracks, Speakers, Sessions, Schedule ---


@router.get("/{event_id}/schedule", response_model=FullScheduleOut)
def get_event_schedule(event_id: str, db: Session = Depends(get_db)):
    event = db.get(
        Event,
        event_id,
        options=[
            selectinload(Event.tracks),
            selectinload(Event.sessions).selectinload(SessionModel.track),
            selectinload(Event.sessions).selectinload(SessionModel.speaker),
        ],
    )
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

    tracks_out = [TrackOut.model_validate(t) for t in sorted(event.tracks, key=lambda t: t.order)]

    # Group sessions by date
    days_dict: dict[str, list[SessionModel]] = {}
    for s in sorted(event.sessions, key=lambda x: x.start_time):
        day_key = s.start_time.strftime("%Y-%m-%d")
        days_dict.setdefault(day_key, []).append(s)

    schedule_days: list[ScheduleDay] = []
    day_count = 1
    for day_str, day_sessions in sorted(days_dict.items(), key=lambda x: x[0]):
        parsed_date = datetime.strptime(day_str, "%Y-%m-%d")
        date_label = f"Day {day_count} — {parsed_date.strftime('%A, %b %d')}"
        day_count += 1

        # Group into time slots
        slots_dict: dict[str, tuple[datetime, datetime, list[SessionModel]]] = {}
        for s in day_sessions:
            time_key = f"{s.start_time.isoformat()}_{s.end_time.isoformat()}"
            if time_key not in slots_dict:
                slots_dict[time_key] = (s.start_time, s.end_time, [])
            slots_dict[time_key][2].append(s)

        slots: list[ScheduleSlot] = []
        for _, (st, et, slot_sessions) in sorted(slots_dict.items(), key=lambda x: x[1][0]):
            time_label = f"{st.strftime('%I:%M %p')} - {et.strftime('%I:%M %p')}"
            slots.append(
                ScheduleSlot(
                    time_label=time_label,
                    start_time=st,
                    end_time=et,
                    sessions=[SessionOut.model_validate(s) for s in slot_sessions],
                )
            )

        schedule_days.append(
            ScheduleDay(
                date=day_str,
                date_label=date_label,
                tracks=tracks_out,
                slots=slots,
            )
        )

    if not schedule_days:
        schedule_days.append(
            ScheduleDay(
                date=event.starts_at.strftime("%Y-%m-%d"),
                date_label=f"Day 1 — {event.starts_at.strftime('%A, %b %d')}",
                tracks=tracks_out,
                slots=[],
            )
        )

    return FullScheduleOut(
        event_id=event.id,
        event_title=event.title,
        days=schedule_days,
    )


@router.get("/{event_id}/speakers", response_model=list[SpeakerWithSessionsOut])
def get_event_speakers(event_id: str, db: Session = Depends(get_db)):
    event = db.get(
        Event,
        event_id,
        options=[
            selectinload(Event.speakers).selectinload(Speaker.sessions).selectinload(SessionModel.track),
        ],
    )
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return sorted(event.speakers, key=lambda s: s.name)


@router.get("/{event_id}/tracks", response_model=list[TrackOut])
def get_event_tracks(event_id: str, db: Session = Depends(get_db)):
    event = db.get(Event, event_id, options=[selectinload(Event.tracks)])
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")
    return sorted(event.tracks, key=lambda t: t.order)


@router.post("/{event_id}/tracks", response_model=TrackOut, status_code=status.HTTP_201_CREATED)
def add_track(event_id: str, payload: TrackCreate, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    track = Track(
        event_id=event.id,
        name=payload.name,
        description=payload.description,
        room_location=payload.room_location,
        color_code=payload.color_code,
        order=payload.order,
    )
    db.add(track)
    db.commit()
    db.refresh(track)
    return track


@router.post("/{event_id}/speakers", response_model=SpeakerOut, status_code=status.HTTP_201_CREATED)
def add_speaker(event_id: str, payload: SpeakerCreate, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    speaker = Speaker(
        event_id=event.id,
        name=payload.name,
        role_title=payload.role_title,
        company=payload.company,
        bio=payload.bio,
        avatar_url=payload.avatar_url,
        github_url=payload.github_url,
        twitter_url=payload.twitter_url,
        linkedin_url=payload.linkedin_url,
    )
    db.add(speaker)
    db.commit()
    db.refresh(speaker)
    return speaker


@router.post("/{event_id}/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def add_session(event_id: str, payload: SessionCreate, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    event = _get_owned_event(event_id, user, db)
    session = SessionModel(
        event_id=event.id,
        track_id=payload.track_id,
        speaker_id=payload.speaker_id,
        title=payload.title,
        abstract=payload.abstract,
        session_type=payload.session_type,
        start_time=payload.start_time,
        end_time=payload.end_time,
        slides_url=payload.slides_url,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/seed-demo", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def seed_demo_conference(db: Session = Depends(get_db)):
    """Convenience endpoint to bootstrap the DevSummit flagship conference with tracks, speakers, and schedule."""
    from ..seed_conference import seed_conference_data

    event = seed_conference_data(db)
    # Re-fetch with full relations
    return get_event(event.id, db=db, user=None)
