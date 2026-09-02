import logging

from eventsphere_common.bus import consume_forever
from eventsphere_common.events import EventEnvelope

from .database import SessionLocal
from .models import Notification, ProcessedEvent, SimulatedEmail

logger = logging.getLogger("eventsphere.notification.worker")

# event_type -> (title_template, body_template, notification_type)
TEMPLATES = {
    "BookingConfirmed": ("Booking confirmed", "Your booking {booking_id} for this event is confirmed. Amount paid: INR {amount}.", "BOOKING_CONFIRMED"),
    "PaymentSucceeded": ("Payment received", "We received your payment of INR {amount} for booking {booking_id}.", "PAYMENT_SUCCEEDED"),
    "PaymentFailed": ("Payment failed", "Your payment for booking {booking_id} could not be completed. You can try again before your reservation expires.", "PAYMENT_FAILED"),
    "BookingCancelled": ("Booking cancelled", "Your booking {booking_id} has been cancelled.", "BOOKING_CANCELLED"),
    "BookingExpired": ("Reservation expired", "Your ticket reservation {booking_id} expired before payment was completed. The tickets have been released.", "BOOKING_EXPIRED"),
    "EventUpdated": ("Event updated", "An event you're interested in has been updated.", "EVENT_UPDATED"),
    "EventCancelled": ("Event cancelled: {title}", "Unfortunately '{title}' has been cancelled by the organizer. Any paid bookings will be automatically refunded.", "EVENT_CANCELLED"),
    "RefundProcessed": ("Refund processed", "Your refund of INR {amount} for booking {booking_id} has been processed.", "REFUND_PROCESSED"),
}

# Which field in the event's `data` payload carries the recipient user_id.
RECIPIENT_FIELD = {
    "BookingConfirmed": "user_id",
    "PaymentSucceeded": "user_id",
    "PaymentFailed": "user_id",
    "BookingCancelled": "user_id",
    "BookingExpired": "user_id",
    "EventUpdated": "organizer_id",
    "EventCancelled": "organizer_id",
    "RefundProcessed": "user_id",
}


def handle_event(envelope: EventEnvelope) -> None:
    db = SessionLocal()
    try:
        if db.get(ProcessedEvent, envelope.event_id):
            return  # already handled -> at-least-once delivery, idempotent no-op

        template = TEMPLATES.get(envelope.event_type)
        if not template:
            db.add(ProcessedEvent(event_id=envelope.event_id))
            db.commit()
            return

        title_tpl, body_tpl, notif_type = template
        recipient_field = RECIPIENT_FIELD.get(envelope.event_type, "user_id")
        recipient = envelope.data.get(recipient_field)
        if not recipient:
            db.add(ProcessedEvent(event_id=envelope.event_id))
            db.commit()
            return

        safe_data = {k: v for k, v in envelope.data.items()}
        title = title_tpl.format(**safe_data) if "{" in title_tpl else title_tpl
        body = body_tpl.format(**safe_data) if "{" in body_tpl else body_tpl

        db.add(Notification(user_id=recipient, type=notif_type, title=title, body=body))
        db.add(SimulatedEmail(to_user_id=recipient, subject=title, body=body))
        db.add(ProcessedEvent(event_id=envelope.event_id))
        db.commit()

        logger.info("[SIMULATED EMAIL] to=%s subject=%r body=%r", recipient, title, body)
    finally:
        db.close()


def run_worker() -> None:
    consume_forever(
        queue_name="notification-service.events",
        routing_keys=["eventsphere.#"],
        handler=handle_event,
    )
