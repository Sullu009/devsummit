import os
import sys
import time
import uuid

os.environ["DATABASE_URL"] = "sqlite:////tmp/analytics_test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RABBITMQ_URL"] = os.environ.get("TEST_RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from eventsphere_common.db import Base
from eventsphere_common.security import create_access_token

DB_PATH = "/tmp/analytics_test.db"


@pytest.fixture()
def db_engine():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    from app import models  # noqa: F401
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(bind=engine)
    yield engine
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


@pytest.fixture()
def app_client(db_engine):
    from app import database as db_module
    from app.main import app

    db_module.engine = db_engine
    db_module.SessionLocal.configure(bind=db_engine)
    with TestClient(app) as c:
        yield c


def auth_header(role="ORGANIZER", uid=None):
    uid = uid or str(uuid.uuid4())
    token = create_access_token(uid, role, f"{uid}@example.com")
    return {"Authorization": f"Bearer {token}"}, uid


def test_handle_event_updates_aggregates_directly(db_engine):
    from app.database import SessionLocal
    from app.models import EventStats
    from app.worker import handle_event
    from eventsphere_common.events import EventEnvelope

    event_id = "evt-1"
    organizer_id = "org-1"

    handle_event(EventEnvelope(event_type="EventViewed", source_service="test", data={"event_id": event_id}))
    handle_event(EventEnvelope(event_type="EventViewed", source_service="test", data={"event_id": event_id}))
    handle_event(EventEnvelope(event_type="BookingConfirmed", source_service="test", data={"event_id": event_id, "organizer_id": organizer_id, "ticket_count": 2}))
    handle_event(EventEnvelope(event_type="PaymentSucceeded", source_service="test", data={"event_id": event_id, "organizer_id": organizer_id, "amount": 999.0}))

    db = SessionLocal()
    try:
        stats = db.get(EventStats, event_id)
        assert stats.views == 2
        assert stats.bookings_confirmed == 1
        assert stats.tickets_sold == 2
        assert float(stats.revenue) == 999.0
        assert stats.organizer_id == organizer_id
    finally:
        db.close()


def test_organizer_analytics_api_and_authorization(app_client):
    from app.database import SessionLocal
    from app.models import EventStats

    headers, uid = auth_header("ORGANIZER")
    other_headers, other_uid = auth_header("ORGANIZER")

    db = SessionLocal()
    db.add(EventStats(event_id="evt-2", organizer_id=uid, views=10, bookings_confirmed=2, tickets_sold=3, revenue=1500.0))
    db.commit()
    db.close()

    resp = app_client.get(f"/analytics/organizer/{uid}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["conversion_rate"] == 20.0  # 2 confirmed / 10 views

    forbidden = app_client.get(f"/analytics/organizer/{uid}", headers=other_headers)
    assert forbidden.status_code == 403


def test_worker_processes_real_rabbitmq_event(db_engine):
    import threading

    from app import database as db_module
    from app.database import SessionLocal
    from app.models import EventStats
    from app.worker import run_worker
    from eventsphere_common.bus import publish_event

    db_module.engine = db_engine
    db_module.SessionLocal.configure(bind=db_engine)

    event_id = f"evt-{uuid.uuid4().hex[:8]}"

    t = threading.Thread(target=run_worker, daemon=True)
    t.start()
    time.sleep(1.5)

    publish_event("EventViewed", "test", {"event_id": event_id})

    deadline = time.time() + 6
    stats = None
    db = SessionLocal()
    try:
        while time.time() < deadline:
            stats = db.get(EventStats, event_id)
            if stats and stats.views >= 1:
                break
            db.expire_all()
            time.sleep(0.3)
    finally:
        db.close()

    assert stats is not None
    assert stats.views == 1
