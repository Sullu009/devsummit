from eventsphere_common.auth_deps import CurrentUser, require_roles
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Payment, PaymentStatus
from ..schemas import PaymentOut

router = APIRouter(prefix="/payments", tags=["organizer-revenue"])


@router.get("/events/{event_id}/revenue")
def event_revenue(event_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    stmt = select(Payment).where(Payment.event_id == event_id)
    payments = db.execute(stmt).scalars().all()

    if payments and payments[0].organizer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot view another organizer's revenue")

    succeeded = [p for p in payments if p.status == PaymentStatus.SUCCEEDED]
    failed = [p for p in payments if p.status == PaymentStatus.FAILED]
    refunded = [p for p in payments if p.status == PaymentStatus.REFUNDED]

    gross_revenue = sum(float(p.amount) for p in succeeded) + sum(float(p.amount) for p in refunded)
    refunded_amount = sum(float(p.amount) for p in refunded)
    net_revenue = gross_revenue - refunded_amount
    attempted = len(succeeded) + len(failed) + len(refunded)
    success_rate = round(((len(succeeded) + len(refunded)) / attempted) * 100, 1) if attempted else 0.0

    recent = sorted(payments, key=lambda p: p.created_at, reverse=True)[:20]

    return {
        "event_id": event_id,
        "gross_revenue": round(gross_revenue, 2),
        "net_revenue": round(net_revenue, 2),
        "paid_bookings": len(succeeded) + len(refunded),
        "refunded_count": len(refunded),
        "refunded_amount": round(refunded_amount, 2),
        "payment_failures": len(failed),
        "payment_success_rate": success_rate,
        "recent_transactions": [PaymentOut.model_validate(p).model_dump(mode="json") for p in recent],
    }


@router.get("/organizer/{organizer_id}/summary")
def organizer_summary(organizer_id: str, user: CurrentUser = Depends(require_roles("ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    if organizer_id != user.id and user.role != "ADMIN":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You cannot view another organizer's revenue")

    stmt = select(Payment).where(Payment.organizer_id == organizer_id)
    payments = db.execute(stmt).scalars().all()
    succeeded = [p for p in payments if p.status in (PaymentStatus.SUCCEEDED, PaymentStatus.REFUNDED)]
    total_revenue = sum(float(p.amount) for p in succeeded)

    by_event: dict[str, float] = {}
    for p in succeeded:
        by_event[p.event_id] = by_event.get(p.event_id, 0) + float(p.amount)

    return {
        "organizer_id": organizer_id,
        "total_revenue": round(total_revenue, 2),
        "total_paid_bookings": len(succeeded),
        "revenue_by_event": {k: round(v, 2) for k, v in by_event.items()},
    }
