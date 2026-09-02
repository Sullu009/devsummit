# Testing

EventSphere's automated tests live **inside each service** (`services/<name>/tests/`) rather than in
this top-level directory, because each service has its own dependencies, its own database, and
needs to be runnable/testable in isolation — that's the point of a microservices split. This file
is a map to all of them.

## Running everything

```bash
for svc in identity-service event-service booking-service payment-service \
           notification-service refund-service analytics-service; do
  (cd services/$svc && pip install -r requirements.txt && pytest)
done
(cd api-gateway && pip install -r requirements.txt && pytest)
```

`booking-service`, `notification-service`, `refund-service`, and `analytics-service` need a local
Redis and/or RabbitMQ reachable (see their `tests/conftest.py` for the `TEST_REDIS_URL` /
`TEST_RABBITMQ_URL` env vars, which default to `localhost`) — the rest run against in-memory
SQLite with no external dependencies.

## What's covered

| Service | Coverage |
|---|---|
| identity-service | registration, login, wrong-password rejection, duplicate-email rejection, admin-only user listing |
| event-service | draft→publish→cancel state machine, ownership checks, publish requires ≥1 ticket type, idempotent internal stock decrement |
| booking-service | reservation + sold-out handling, cancel releases hold, ownership check, **10 concurrent threads racing for the last ticket against real Redis — exactly 1 succeeds** |
| payment-service | order creation, cross-account payment rejection, real HMAC signature verification (valid + tampered), idempotent verify replay |
| notification-service | event→notification+simulated-email translation, idempotent duplicate delivery, real RabbitMQ publish→consume round trip |
| refund-service | manual refund trigger, idempotent replay (Razorpay refund call only fires once), 404 on missing payment, real RabbitMQ-driven refund flow |
| analytics-service | aggregate updates from domain events, organizer authorization, real RabbitMQ-driven aggregate update |
| api-gateway | route resolution to the correct downstream service, sliding-window rate limiter behavior |

## Frontend

The frontend has no dedicated Playwright suite in this build — `npm run build` (which
includes full TypeScript type-checking across all 21 routes) is the current build-time
safety net. Adding a Playwright E2E suite covering the
register → login → browse → reserve → checkout → payment → confirmation flow described in
the project brief is the natural next step; `frontend/src/lib/api.ts` and
`frontend/src/lib/types.ts` are written to make that straightforward to wire up against a
running `docker compose` stack.
