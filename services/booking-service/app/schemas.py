from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import BookingStatus


class ReserveItem(BaseModel):
    ticket_type_id: str
    quantity: int = Field(gt=0, le=20)


class ReserveRequest(BaseModel):
    event_id: str
    items: list[ReserveItem] = Field(min_length=1)


class BookingItemOut(BaseModel):
    id: str
    ticket_type_id: str
    ticket_type_name: str
    unit_price: Decimal
    quantity: int

    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: str
    reservation_id: str
    user_id: str
    event_id: str
    organizer_id: str
    status: BookingStatus
    total_amount: Decimal
    expires_at: datetime | None
    created_at: datetime
    items: list[BookingItemOut]

    model_config = {"from_attributes": True}
