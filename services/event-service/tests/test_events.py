import os

os.environ["JWT_SECRET"] = "test-secret"

from datetime import datetime, timedelta, timezone

from eventsphere_common.security import create_access_token

ORGANIZER_ID = "org-1"
OTHER_ORGANIZER_ID = "org-2"
ATTENDEE_ID = "att-1"


def _token(uid, role, email="x@example.com"):
    return create_access_token(uid, role, email)


def _auth(uid, role):
    return {"Authorization": f"Bearer {_token(uid, role)}"}


def _event_payload():
    starts = datetime.now(timezone.utc) + timedelta(days=30)
    ends = starts + timedelta(hours=4)
    sale_start = datetime.now(timezone.utc) - timedelta(days=1)
    sale_end = starts - timedelta(hours=1)
    return {
        "title": "PyCon Muscat",
        "description": "A conference",
        "category": "TECH",
        "venue_name": "Convention Center",
        "venue_address": "123 Main St",
        "city": "Muscat",
        "starts_at": starts.isoformat(),
        "ends_at": ends.isoformat(),
        "ticket_types": [
            {
                "name": "Early Bird", "description": "", "price": "499.00", "quantity_total": 2,
                "sale_starts_at": sale_start.isoformat(), "sale_ends_at": sale_end.isoformat(),
            }
        ],
    }


def test_create_and_publish_flow(client):
    resp = client.post("/events", json=_event_payload(), headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    assert resp.status_code == 201
    event = resp.json()
    assert event["status"] == "DRAFT"

    # not visible to public while draft
    public_list = client.get("/events").json()
    assert event["id"] not in [e["id"] for e in public_list["items"]]

    # only owner can publish
    resp = client.post(f"/events/{event['id']}/publish", headers=_auth(OTHER_ORGANIZER_ID, "ORGANIZER"))
    assert resp.status_code == 403

    resp = client.post(f"/events/{event['id']}/publish", headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    assert resp.status_code == 200
    assert resp.json()["status"] == "PUBLISHED"

    # publishing again is an invalid transition
    resp = client.post(f"/events/{event['id']}/publish", headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    assert resp.status_code == 409

    public_list = client.get("/events").json()
    assert event["id"] in [e["id"] for e in public_list["items"]]


def test_publish_requires_ticket_type(client):
    payload = _event_payload()
    payload["ticket_types"] = []
    resp = client.post("/events", json=payload, headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    event = resp.json()
    resp = client.post(f"/events/{event['id']}/publish", headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    assert resp.status_code == 400


def test_internal_decrement_is_idempotent(client):
    resp = client.post("/events", json=_event_payload(), headers=_auth(ORGANIZER_ID, "ORGANIZER"))
    event = resp.json()
    tt_id = event["ticket_types"][0]["id"]

    body = {"quantity": 1, "idempotency_key": "book-1"}
    r1 = client.post(f"/internal/ticket-types/{tt_id}/decrement", json=body)
    assert r1.json()["quantity_available"] == 1

    # retry with same idempotency key must not double-decrement
    r2 = client.post(f"/internal/ticket-types/{tt_id}/decrement", json=body)
    assert r2.json()["quantity_available"] == 1
