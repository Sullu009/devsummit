import os
import sys
import uuid

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["REDIS_URL"] = os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/0")

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
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    yield engine


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

    # Flush Redis so tests don't leak holds into each other.
    from app.redis_holds import ticket_hold_store
    ticket_hold_store._client.flushdb()

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def mock_event_service(monkeypatch):
    """In-memory fake of the Event Service's internal API surface used by booking-service."""
    state = {"tickets": {}, "events": {}}

    def seed_ticket(ticket_type_id, name="General", price=500.0, quantity_available=10):
        state["tickets"][ticket_type_id] = {
            "id": ticket_type_id, "name": name, "description": "", "price": price,
            "quantity_total": quantity_available, "quantity_available": quantity_available,
        }

    def seed_event(event_id, organizer_id="org-1", status="PUBLISHED"):
        state["events"][event_id] = {"id": event_id, "organizer_id": organizer_id, "status": status, "title": "Test Event"}

    from app import event_client

    def get_ticket_type(self, ticket_type_id):
        return state["tickets"].get(ticket_type_id)

    def get_event_summary(self, event_id):
        return state["events"].get(event_id)

    def decrement_availability(self, ticket_type_id, quantity, idempotency_key):
        t = state["tickets"][ticket_type_id]
        t["quantity_available"] -= quantity
        return t

    def increment_availability(self, ticket_type_id, quantity, idempotency_key):
        t = state["tickets"][ticket_type_id]
        t["quantity_available"] += quantity
        return t

    monkeypatch.setattr(event_client.EventServiceClient, "get_ticket_type", get_ticket_type)
    monkeypatch.setattr(event_client.EventServiceClient, "get_event_summary", get_event_summary)
    monkeypatch.setattr(event_client.EventServiceClient, "decrement_availability", decrement_availability)
    monkeypatch.setattr(event_client.EventServiceClient, "increment_availability", increment_availability)

    state["seed_ticket"] = seed_ticket
    state["seed_event"] = seed_event
    return state


def auth_header(role="ATTENDEE", uid=None):
    uid = uid or str(uuid.uuid4())
    token = create_access_token(uid, role, f"{uid}@example.com")
    return {"Authorization": f"Bearer {token}"}, uid
