import os
import sys
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RAZORPAY_KEY_ID"] = "rzp_test_fake"
os.environ["RAZORPAY_KEY_SECRET"] = "fake_secret"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from eventsphere_common.db import Base
from eventsphere_common.security import create_access_token


@pytest.fixture()
def db_engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)


@pytest.fixture()
def client(db_engine, monkeypatch):
    from app import database as db_module
    from app.main import app

    Base.metadata.create_all(bind=db_engine)
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False, expire_on_commit=False)
    db_module.SessionLocal.configure(bind=db_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[db_module.get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def mock_razorpay(monkeypatch):
    from app import razorpay_client

    def create_order(amount, receipt, notes):
        return {"id": f"order_{uuid.uuid4().hex[:12]}", "amount": razorpay_client.to_paise(amount), "currency": "INR"}

    monkeypatch.setattr(razorpay_client, "create_order", create_order)


@pytest.fixture()
def mock_booking_service(monkeypatch):
    """Fakes booking-service: one PENDING_PAYMENT booking, confirm() flips it to CONFIRMED."""
    state = {"bookings": {}, "confirmed": []}

    def seed_booking(booking_id, user_id, organizer_id="org-1", event_id="evt-1", amount=1000.0, status="PENDING_PAYMENT"):
        state["bookings"][booking_id] = {
            "id": booking_id, "user_id": user_id, "organizer_id": organizer_id, "event_id": event_id,
            "total_amount": amount, "status": status,
        }

    from app import booking_client

    def get_booking(self, booking_id, auth_header):
        return state["bookings"].get(booking_id)

    def confirm_booking(self, booking_id, payment_id):
        b = state["bookings"][booking_id]
        b["status"] = "CONFIRMED"
        state["confirmed"].append(booking_id)
        return b

    monkeypatch.setattr(booking_client.BookingServiceClient, "get_booking", get_booking)
    monkeypatch.setattr(booking_client.BookingServiceClient, "confirm_booking", confirm_booking)

    state["seed_booking"] = seed_booking
    return state


def auth_header(role="ATTENDEE", uid=None):
    uid = uid or str(uuid.uuid4())
    token = create_access_token(uid, role, f"{uid}@example.com")
    return {"Authorization": f"Bearer {token}"}, uid
