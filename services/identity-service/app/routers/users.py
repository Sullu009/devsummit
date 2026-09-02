from eventsphere_common.auth_deps import CurrentUser, require_roles
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), _: CurrentUser = Depends(require_roles("ADMIN"))):
    return db.execute(select(User).order_by(User.created_at.desc())).scalars().all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Unauthenticated lookup by ID for service-to-service use (name/email display only)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user
