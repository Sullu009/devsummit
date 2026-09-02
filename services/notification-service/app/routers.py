from datetime import datetime

from eventsphere_common.auth_deps import CurrentUser, get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: str
    type: str
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[NotificationOut])
def list_notifications(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db), unread_only: bool = False):
    stmt = select(Notification).where(Notification.user_id == user.id)
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    stmt = stmt.order_by(Notification.created_at.desc())
    return db.execute(stmt).scalars().all()


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: str, user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.get(Notification, notification_id)
    if not notif or notif.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(Notification).where(Notification.user_id == user.id, Notification.is_read.is_(False))
    for n in db.execute(stmt).scalars().all():
        n.is_read = True
    db.commit()
    return None
