import os
import sys
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RABBITMQ_URL"] = os.environ.get("TEST_RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")

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
def client(db_engine):
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
def mock_clients(monkeypatch):
    state = {"payments": {}, "refund_calls": [], "booking_marked_refunded": []}

    def seed_payment(payment_id, booking_id, user_id, amount=500.0):
        state["payments"][booking_id] = {"id": payment_id, "booking_id": booking_id, "user_id": user_id, "amount": amount, "status": "SUCCEEDED"}

    from app import clients

    def get_payment_for_booking(self, booking_id):
        return state["payments"].get(booking_id)

    def process_refund(self, payment_id):
        state["refund_calls"].append(payment_id)
        return {"status": "refunded", "razorpay_refund_id": f"rfnd_{uuid.uuid4().hex[:10]}"}

    def mark_refunded(self, booking_id):
        state["booking_marked_refunded"].append(booking_id)

    def mark_refund_pending(self, booking_id):
        pass

    def get_bookings_by_event(self, event_id, booking_status=None):
        return []

    monkeypatch.setattr(clients.PaymentServiceClient, "get_payment_for_booking", get_payment_for_booking)
    monkeypatch.setattr(clients.PaymentServiceClient, "process_refund", process_refund)
    monkeypatch.setattr(clients.BookingServiceClient, "mark_refunded", mark_refunded)
    monkeypatch.setattr(clients.BookingServiceClient, "mark_refund_pending", mark_refund_pending)
    monkeypatch.setattr(clients.BookingServiceClient, "get_bookings_by_event", get_bookings_by_event)

    state["seed_payment"] = seed_payment
    return state


def auth_header(role="ATTENDEE", uid=None):
    uid = uid or str(uuid.uuid4())
    token = create_access_token(uid, role, f"{uid}@example.com")
    return {"Authorization": f"Bearer {token}"}, uid
