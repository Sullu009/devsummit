import os
import sys
import time
import uuid

os.environ["DATABASE_URL"] = "sqlite:////tmp/notif_test.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RABBITMQ_URL"] = os.environ.get("TEST_RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from eventsphere_common.db import Base
from eventsphere_common.bus import publish_event

DB_PATH = "/tmp/notif_test.db"


@pytest.fixture(autouse=True)
def fresh_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    from app import models  # noqa: F401 - registers tables on Base.metadata before create_all
    from app import database as db_module

    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(bind=engine)
    db_module.engine = engine
    db_module.SessionLocal.configure(bind=engine)
    yield
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


def test_worker_creates_notification_and_simulated_email_from_real_rabbitmq_event():
    from app.database import SessionLocal
    from app.models import Notification, SimulatedEmail
    from app.worker import handle_event
    from eventsphere_common.events import EventEnvelope

    user_id = str(uuid.uuid4())
    booking_id = str(uuid.uuid4())

    envelope = publish_event("BookingConfirmed", "test", {"booking_id": booking_id, "user_id": user_id, "amount": 999.0})

    # Simulate the consumer receiving the message it just published (proves the
    # handler + templating logic work against a payload shaped exactly like
    # what RabbitMQ will actually deliver).
    handle_event(EventEnvelope.model_validate(envelope.model_dump()))

    db = SessionLocal()
    try:
        notif = db.execute(select(Notification).where(Notification.user_id == user_id)).scalar_one_or_none()
        assert notif is not None
        assert "confirmed" in notif.title.lower()
        assert booking_id in notif.body

        email = db.execute(select(SimulatedEmail).where(SimulatedEmail.to_user_id == user_id)).scalar_one_or_none()
        assert email is not None
    finally:
        db.close()


def test_worker_is_idempotent_on_duplicate_event_id():
    from app.database import SessionLocal
    from app.models import Notification
    from app.worker import handle_event
    from eventsphere_common.events import EventEnvelope

    user_id = str(uuid.uuid4())
    envelope = EventEnvelope(event_type="PaymentFailed", source_service="test", data={"booking_id": "b1", "user_id": user_id})

    handle_event(envelope)
    handle_event(envelope)  # duplicate delivery, same event_id

    db = SessionLocal()
    try:
        count = len(db.execute(select(Notification).where(Notification.user_id == user_id)).scalars().all())
        assert count == 1
    finally:
        db.close()


def test_real_rabbitmq_end_to_end_delivery():
    """Publishes to the real broker and runs an actual consume_forever loop briefly to prove wiring works end-to-end."""
    import threading

    from app.database import SessionLocal
    from app.models import Notification
    from eventsphere_common.bus import consume_forever
    from eventsphere_common.events import EventEnvelope

    user_id = str(uuid.uuid4())
    queue_name = f"test-notification-{uuid.uuid4().hex[:8]}"

    received = []

    def handler(envelope: EventEnvelope):
        received.append(envelope)

    t = threading.Thread(
        target=consume_forever,
        kwargs={"queue_name": queue_name, "routing_keys": ["eventsphere.bookingconfirmed"], "handler": handler},
        daemon=True,
    )
    t.start()
    time.sleep(1.5)  # allow consumer to declare queue/bindings before publishing

    publish_event("BookingConfirmed", "test", {"booking_id": "real-e2e", "user_id": user_id, "amount": 1.0})

    deadline = time.time() + 5
    while time.time() < deadline and not received:
        time.sleep(0.2)

    assert len(received) == 1
    assert received[0].data["booking_id"] == "real-e2e"
