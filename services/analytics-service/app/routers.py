from eventsphere_common.auth_deps import CurrentUser, require_roles
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import EventStats

router = APIRouter(prefix="/analytics", tags=["analytics"])


class EventStatsOut(BaseModel):
    event_id: str
    views: int
    bookings_created: int
    bookings_confirmed: int
    bookings_cancelled: int
    tickets_sold: int
    revenue: float
    attendance_count: int
    conversion_rate: float

    model_config = {"from_attributes": True}


def _to_out(stats: EventStats) -> EventStatsOut:
    conversion = round((stats.bookings_confirmed / stats.views) * 100, 1) if stats.views else 0.0
    return EventStatsOut(
        event_id=stats.event_id, views=stats.views, bookings_created=stats.bookings_created,
        bookings_confirmed=stats.bookings_confirmed, bookings_cancelled=stats.bookings_cancelled,
        tickets_sold=stats.tickets_sold, revenue=float(stats.revenue), attendance_count=stats.attendance_count,
        conversion_rate=conversion,
    )


@router.get("/events/{event_id}", response_model=EventStatsOut)
def get_event_analytics(event_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    stats = db.get(EventStats, event_id)
    if not stats:
        return EventStatsOut(event_id=event_id, views=0, bookings_created=0, bookings_confirmed=0, bookings_cancelled=0, tickets_sold=0, revenue=0, attendance_count=0, conversion_rate=0)
    if stats.organizer_id and stats.organizer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot view analytics for another organizer's event")
    return _to_out(stats)


@router.get("/organizer/{organizer_id}", response_model=list[EventStatsOut])
def get_organizer_analytics(organizer_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    if organizer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot view another organizer's analytics")
    stmt = select(EventStats).where(EventStats.organizer_id == organizer_id)
    return [_to_out(s) for s in db.execute(stmt).scalars().all()]


@router.get("/platform/summary")
def platform_summary(user: CurrentUser = Depends(require_roles("ADMIN")), db: Session = Depends(get_db)):
    all_stats = db.execute(select(EventStats)).scalars().all()
    return {
        "total_events_tracked": len(all_stats),
        "total_views": sum(s.views for s in all_stats),
        "total_bookings_confirmed": sum(s.bookings_confirmed for s in all_stats),
        "total_tickets_sold": sum(s.tickets_sold for s in all_stats),
        "total_revenue": round(sum(float(s.revenue) for s in all_stats), 2),
    }
