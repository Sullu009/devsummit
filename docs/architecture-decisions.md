# Architecture Decision Notes

Short-form record of the non-obvious calls made while building EventSphere, for the
mentor/engineer walkthrough mentioned in the project brief.

## 1. One Postgres server, one database per service
Full physical isolation (one RDS instance per service) is the "more correct" answer at
large scale, but at this project's scale it's pure operational overhead for zero
practical benefit — nothing here is multi-tenant or has per-service compliance
boundaries that demand it. Logical database isolation still gets you the thing that
actually matters: no service can query another's tables directly, so the service
boundary is real in the code, not just in folder structure. See `infrastructure/postgres/init-databases.sh`.

## 2. Redis holds vs. reserving in Postgres directly
Ticket reservations are high-churn, short-lived (10 min TTL), and don't need to survive
a Postgres restart — that's exactly what Redis is for. Doing the atomic
check-and-increment in Postgres would mean row-level locking under contention on the
single hottest row in the whole system (the ticket_types row for a popular event's last
few tickets); a Redis Lua script does the same atomic check-and-set without touching
Postgres until a payment actually succeeds. Postgres remains the source of truth for
anything that must survive a restart (the Booking row itself, its status, its expiry
time) — Redis only ever holds the *soft* reservation.

## 3. Sync HTTP for reads-you-need-now, async events for everything else
Booking Service calling Event Service synchronously to check ticket availability is a
case where the caller genuinely cannot proceed without the answer. Notification Service
finding out a booking was confirmed is not — it's fine for that to happen 200ms later
via a queue. Mixing these up in either direction (making booking reservation
async-eventually-consistent, or making notification sending block the checkout request)
would make the system either incorrect or slow for no benefit.

## 4. Payment Service, not Booking Service, owns Razorpay
Booking Service knows about reservations and inventory; it has no reason to also know
about signature verification, webhook payloads, or refund API calls. Splitting payment
concerns into their own service means Razorpay's API surface (and its TEST-MODE-only
credentials) touches exactly one service's codebase, and that service's only external
dependency (besides Postgres) is Razorpay's API — easy to reason about, easy to swap
providers later without touching booking logic at all.

## 5. Idempotency is enforced at every async boundary, not just payments
RabbitMQ's at-least-once delivery guarantee means every consumer *will* eventually see
a duplicate message in production, not hypothetically. Rather than trusting each
consumer to independently get this right, every consumer in this codebase follows the
same pattern: a `processed_events(event_id)` table checked before doing anything, and
either no-ops or returns the previous result on a repeat. Same idea applies to the
booking-confirm and refund-process endpoints, which are called over plain HTTP where a
client retry after a timeout is just as likely as a queue redelivery.
