from datetime import datetime
from decimal import Decimal

from eventsphere_common.auth_deps import CurrentUser, require_roles
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Refund, RefundStatus
from .refund_logic import process_refund_for_booking

router = APIRouter(prefix="/refunds", tags=["refunds"])


class RefundOut(BaseModel):
    id: str
    booking_id: str
    payment_id: str
    user_id: str
    amount: Decimal
    reason: str
    status: RefundStatus
    razorpay_refund_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ManualRefundRequest(BaseModel):
    booking_id: str
    reason: str = "Manual refund"


@router.post("", response_model=RefundOut, status_code=status.HTTP_201_CREATED)
def trigger_refund(payload: ManualRefundRequest, user: CurrentUser = Depends(require_roles("ATTENDEE", "ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    """
    Manual/synchronous refund trigger. In normal operation, attendee
    cancellations flow asynchronously via RefundRequested -> this
    service's RabbitMQ consumer; this endpoint exists for
    organizer/admin-initiated refunds and for tests/support tooling.
    """
    try:
        refund = process_refund_for_booking(db, payload.booking_id, reason=payload.reason)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    if refund.user_id != user.id and user.role not in ("ORGANIZER", "ADMIN"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    return refund


@router.get("/{refund_id}", response_model=RefundOut)
def get_refund(refund_id: str, user: CurrentUser = Depends(require_roles("ATTENDEE", "ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    refund = db.get(Refund, refund_id)
    if not refund:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Refund not found")
    if refund.user_id != user.id and user.role not in ("ORGANIZER", "ADMIN"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")
    return refund


@router.get("", response_model=list[RefundOut])
def list_my_refunds(user: CurrentUser = Depends(require_roles("ATTENDEE", "ORGANIZER", "ADMIN")), db: Session = Depends(get_db)):
    stmt = select(Refund).where(Refund.user_id == user.id).order_by(Refund.created_at.desc())
    return db.execute(stmt).scalars().all()
