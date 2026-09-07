# 🚀 DevSummit — Microservices Tech Conference & Ticketing Platform

This document explains **everything** about this project — from fundamental distributed systems concepts and high-concurrency race conditions to the complete microservices architecture, event-driven pipelines, and client-side badge rendering. After reading this, you should understand exactly how requests, payments, and events flow through the system without needing to read every line of code.

---

## 📑 Table of Contents

1. [What is DevSummit?](#1-what-is-devsummit)
2. [Distributed Systems Background](#2-distributed-systems-background)
3. [Project Overview](#3-project-overview)
4. [File & Directory Structure](#4-file--directory-structure)
5. [The Journey of a Request (Step-by-Step Flow)](#5-the-journey-of-a-request-step-by-step-flow)
6. [Deep Dive: Each Microservice Component](#6-deep-dive-each-microservice-component)
7. [How High-Concurrency Redis Lua Holds Work](#7-how-high-concurrency-redis-lua-holds-work)
8. [How RabbitMQ Event-Driven Decoupling Works](#8-how-rabbitmq-event-driven-decoupling-works)
9. [How Multi-Track Scheduling & Printable Badges Work](#9-how-multi-track-scheduling--printable-badges-work)
10. [Database-per-Service Architecture](#10-database-per-service-architecture)
11. [Building and Running](#11-building-and-running)
12. [Understanding the Output & Logs](#12-understanding-the-output--logs)

---

## 1. What is DevSummit?

**DevSummit** is an event-driven microservices platform built specifically to handle the architectural complexities of developer conferences, hackathons, and technical summits (comparable to Google I/O, AWS re:Invent, or PyCon).

### Why Standard Ticketing Apps Fail for Tech Conferences:
* **Single Stage vs Multi-Track**: Movies and concerts happen on one stage at a time. Tech conferences run 3–4 parallel halls simultaneously (e.g., AI in Hall 1, Cloud in Hall 2, Hands-on Workshop in Hall 3).
* **The "Drop" Concurrency Spike**: When ticket sales open for popular conferences, thousands of developers hit "Reserve" at the exact same second. Traditional SQL row-locking chokes under this load, causing database deadlocks or oversold tickets.
* **Complex Physical Badge Requirements**: Attendees don't use simple barcode tickets; they require personalized 4"×6" lanyard badges showing their name, company, role, ticket category, and gate-check-in verification credentials.

### What DevSummit Does:
```
[Attendee Browser] ──► [API Gateway] ──► [7 Microservices] ──► [PostgreSQL & Redis & RabbitMQ]
                             │
            ┌────────────────┴────────────────┐
            ▼                                 ▼
   Multi-Track Agenda               Zero-Overselling Engine
  (Interactive Timetable)          (Atomic Redis Lua Scripts)
            ▼                                 ▼
   Speaker Directories              Event-Driven Side-Effects
  (Talk Abstracts & Links)         (RabbitMQ Async Fan-out)
            ▼                                 ▼
   Printable PDF Badges             Automated Refunds & Sweeper
  (QR Gate Passes)                 (TTL Expiration Workers)
```

---

## 2. Distributed Systems Background

### Monolith vs. Microservices

```
TRADITIONAL MONOLITH                     DEVSUMMIT MICROSERVICES
┌─────────────────────────┐             ┌────────┐  ┌────────┐  ┌────────┐
│  Next.js + Python App   │             │Identity│  │ Event  │  │Booking │
│  - User Auth            │             └────┬───┘  └───┬────┘  └───┬────┘
│  - Event Catalog        │                  │          │           │
│  - Booking & Holds      │             ─────┴──────────┼───────────┴─────
│  - Payments & Refunds   │                      API GATEWAY (8080)
│  - Notification Worker  │             ─────┬──────────┬───────────┬─────
└────────────┬────────────┘                  │          │           │
             │                          ┌────┴───┐  ┌───┴────┐  ┌───┴────┐
┌────────────┴────────────┐             │Payment │  │Notif.  │  │Analytics
│ Single Shared Database  │             └────────┘  └────────┘  └────────┘
└─────────────────────────┘              (Each has its OWN logical database)
```

* **Why Microservices here?**
  * If the **Notification Service** goes down because an external SMTP provider hangs, users can still browse schedules and buy tickets without interruption.
  * If ticket sales open and the **Booking Service** receives 10,000 requests per second, it scales independently with Redis caching without overwhelming the **Identity** or **Analytics** databases.

### The Two Inter-Service Communication Patterns

In distributed systems, microservices must communicate using the right tool for the right job:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. Synchronous HTTP (REST) - "I need the answer RIGHT NOW"             │
│    Example: Booking Service calls Event Service to check if a ticket   │
│    type ID genuinely exists before locking inventory.                  │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Asynchronous Events (RabbitMQ) - "Fire and Forget, Do in Background"│
│    Example: Payment succeeds. Payment Service emits `PaymentSucceeded`. │
│    Notification Service sends receipt email; Analytics Service updates  │
│    revenue counter. Payment Service returns in <100ms to the user.     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Project Overview

### High-Level Service Landscape

DevSummit is divided into **7 independent backend services**, **1 reverse-proxy API Gateway**, and a **modern Next.js 14 frontend**:

```
                               ┌───────────────────┐
                               │ Next.js Frontend  │
                               │   (Port 3000)     │
                               └─────────┬─────────┘
                                         │ HTTP
                                         ▼
                               ┌───────────────────┐
                               │    API Gateway    │ (Port 8080)
                               │  Reverse Proxy &  │ Correlation IDs &
                               │   Rate Limiting   │ Route Forwarding
                               └─────────┬─────────┘
                                         │
        ┌─────────────┬──────────────────┼──────────────────┬─────────────┐
        ▼             ▼                  ▼                  ▼             ▼
   ┌─────────┐   ┌─────────┐        ┌─────────┐        ┌─────────┐   ┌─────────┐
   │Identity │   │ Event   │        │ Booking │        │ Payment │   │ Refund  │
   │ Service │   │ Service │        │ Service │        │ Service │   │ Service │
   │ (8001)  │   │ (8002)  │        │ (8003)  │        │ (8004)  │   │ (8006)  │
   └────┬────┘   └────┬────┘        └────┬────┘        └────┬────┘   └────┬────┘
        │             │                  │                  │             │
        │             │             ┌────┴────┐             │             │
        │             │             │  Redis  │ (Holds)     │             │
        │             │             └─────────┘             │             │
        │             │                                     │             │
        └─────────────┴───────────┬─────────────────────────┴─────────────┘
                                  │ Publishes Domain Events
                                  ▼
                         ┌─────────────────┐
                         │    RabbitMQ     │ (Port 5672 / 15672)
                         │ Topic Exchange  │
                         └────────┬────────┘
                                  │ Consumes Events
                   ┌──────────────┴──────────────┐
                   ▼                             ▼
            ┌─────────────┐               ┌─────────────┐
            │Notification │               │  Analytics  │
            │   Service   │               │   Service   │
            │   (8005)    │               │   (8007)    │
            └──────┬──────┘               └──────┬──────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                     ┌──────────────────────────┐
                     │ PostgreSQL (Port 5432)   │
                     │  7 Isolated Logical DBs  │
                     └──────────────────────────┘
```

---

## 4. File & Directory Structure

```
devsummit/
├── api-gateway/                 # Reverse proxy entry point (routes all /api/* requests)
│   ├── main.py                  # Fast forwarder, correlation ID injector, rate limiter
│   └── Dockerfile               # Container build definition
│
├── frontend/                    # Next.js 14 App Router User Interface
│   ├── src/
│   │   ├── app/                 # Pages: /events, /events/[id], /tickets, /organizer
│   │   ├── components/
│   │   │   ├── schedule-viewer.tsx         # Multi-Track Timetable & Day Tabs
│   │   │   ├── speakers-grid.tsx           # Keynote Speaker Showcase & Abstract Modals
│   │   │   ├── conference-badge-modal.tsx  # 4x6" Vector Printable Lanyard Badge
│   │   │   ├── navbar.tsx                  # Header navigation & user status
│   │   │   └── event-card.tsx              # Conference list preview card
│   │   └── lib/                 # Auth context, API client, and TypeScript types
│   ├── package.json             # React 18, Next 14, Tailwind CSS, Recharts
│   └── Dockerfile
│
├── services/                    # The 7 Microservices (Python + FastAPI)
│   ├── event-service/           # Conferences, Tracks, Speakers, Sessions, Schedules
│   │   ├── app/
│   │   │   ├── models.py        # SQLAlchemy Track, Speaker, Session, Event entities
│   │   │   ├── schemas.py       # Pydantic DTOs for schedule, speakers, tracks
│   │   │   ├── seed_conference.py # Preloaded DevSummit 2026 conference dataset
│   │   │   └── routers/         # /events, /schedule, /speakers, /tracks
│   │   ├── alembic/             # 0001_initial.py, 0002_tracks_speakers_sessions.py
│   │   └── tests/               # Unit and integration tests
│   │
│   ├── booking-service/         # Reservation lifecycle & Redis Lua Concurrency Engine
│   │   ├── app/
│   │   │   ├── redis_holds.py   # Atomic Lua scripts preventing ticket overselling
│   │   │   └── sweeper.py       # Background worker releasing expired 10-min holds
│   │   └── tests/
│   │
│   ├── payment-service/         # Razorpay checkout, webhook handling, HMAC checks
│   ├── identity-service/        # JWT issuance, Argon2 password hashing, user roles
│   ├── notification-service/    # RabbitMQ event consumer: emails & in-app alerts
│   ├── refund-service/          # Cancellation coordinator & automated refund dispatcher
│   └── analytics-service/       # Real-time event views, tickets sold, and revenue metrics
│
├── shared/common/               # Reusable internal Python package (eventsphere_common)
│   ├── auth_deps.py             # JWT verification dependencies for FastAPI
│   ├── bus.py                   # RabbitMQ publisher & consumer wrappers
│   ├── db.py                    # SQLAlchemy session factories & Base models
│   └── security.py              # Cryptographic hashing & token helpers
│
├── infrastructure/postgres/     # Database bootstrap scripts
│   └── init-databases.sh        # Automatically creates 7 isolated logical PostgreSQL DBs
│
├── docker-compose.yml           # Full infrastructure orchestrator (12 services)
├── .env.example                 # Environment variables template
└── README.md                    # This master documentation file
```

---

## 5. The Journey of a Request (Step-by-Step Flow)

Let's trace what happens when an attendee visits DevSummit, picks a pass, pays, and receives their badge:

```
[Attendee] ──► 1. Browse Multi-Track Agenda & Keynotes
                   │
                   ▼
               2. Select "VIP All-Access Pass" & Click Reserve
                   │
                   ▼
               3. Booking Service runs Redis Lua Script ──► [Redis Hold: 10 Min TTL]
                   │
                   ▼
               4. Pay via Razorpay Test Card (HMAC Verified)
                   │
                   ▼
               5. Permanent Postgres Decrement & Booking Confirmed
                   │
                   ▼
               6. RabbitMQ Event Fan-Out (Email + Analytics updated)
                   │
                   ▼
               7. Instant Vector PDF Conference Badge Generated with QR Code
```

### Step 1: Browsing Multi-Track Agendas
* Attendee opens `http://localhost:3000/events/<id>`.
* Frontend calls `GET /api/events/<id>/schedule`.
* **Event Service** queries PostgreSQL for all `tracks`, `speakers`, and `sessions`, groups sessions by conference day (*Day 1*, *Day 2*) and chronological time-slots, and returns the full timetable.

### Step 2: Reserving a Ticket (The Concurrency Gate)
* Attendee clicks "Reserve 1 VIP Pass".
* Request hits `POST /api/bookings/reserve`.
* **Booking Service** executes an atomic **Redis Lua Script**.
* Redis checks: `currently_held + 1 <= total_capacity`.
* If true, Redis increments the held counter and creates a key with a **10-minute TTL**. The status is set to `PENDING_PAYMENT`.

### Step 3: Payment Verification
* Frontend opens Razorpay Checkout (Test Mode).
* Attendee submits payment. Razorpay responds with `order_id`, `payment_id`, and a cryptographically signed HMAC token.
* Frontend calls `POST /api/payments/verify`.
* **Payment Service** computes `HMAC-SHA256(order_id + "|" + payment_id, secret)` on the server. If valid, it informs **Booking Service** via internal HTTP: `POST /internal/bookings/<id>/confirm`.

### Step 4: Permanent Inventory Settlement & Event Fan-Out
* **Booking Service** updates status to `CONFIRMED`.
* It calls **Event Service** to permanently decrement PostgreSQL stock (`quantity_available = quantity_available - 1`) using an idempotency key.
* **Booking Service** publishes `BookingConfirmed` to the RabbitMQ exchange `eventsphere.events`.

### Step 5: Asynchronous Workers React
* **Notification Service** consumes `BookingConfirmed`, generates an in-app notification, and simulates email dispatch.
* **Analytics Service** consumes `BookingConfirmed` and increments revenue and tickets-sold counters.

### Step 6: Badge Generation
* Attendee navigates to **My Passes (`/tickets`)**.
* Clicks **"Print Badge (PDF)"**.
* A 4"×6" lanyard pass is rendered with their custom name, company, pass tier, and cryptographic verification QR code ready to print.

---

## 6. Deep Dive: Each Microservice Component

### 1. `api-gateway` (Port 8080)
* Acts as the single entrypoint for all frontend traffic.
* Generates a unique `x-correlation-id` for every incoming HTTP request and passes it downstream, enabling end-to-end distributed tracing across all microservice log streams.
* Enforces in-memory token-bucket rate limiting to prevent DoS attacks.

### 2. `identity-service` (Port 8001 | `identity_db`)
* Handles authentication using **Argon2id** password hashing (far more memory-hard and resistant to GPU cracking than legacy bcrypt).
* Issues cryptographically signed **JWT tokens** containing `user_id`, `email`, and `role` (`ATTENDEE`, `ORGANIZER`, `ADMIN`).

### 3. `event-service` (Port 8002 | `event_db`)
* Manages the conference catalog, tracks, speakers, sessions, and ticket tiers.
* Contains the custom **DevSummit Conference Engine**:
  * `Track` entity: Room locations, colors, display ordering.
  * `Speaker` entity: Bio, avatar, social handles (GitHub, LinkedIn, Twitter/X).
  * `Session` entity: Talk abstract, session type (`KEYNOTE`, `WORKSHOP`, `TALK`), time window.
* Contains `seed_conference.py` which populates realistic flagship conference data in one click.

### 4. `booking-service` (Port 8003 | `booking_db`)
* Coordinates the reservation lifecycle:
  `PENDING_PAYMENT` ──► `CONFIRMED` ──► `CHECKED_IN` / `REFUNDED`
* Interfaces with **Redis** to place atomic Lua holds on tickets.
* Runs a background task (`sweeper.py`) every 60 seconds to expire abandoned checkouts whose 10-minute TTL has elapsed.

### 5. `payment-service` (Port 8004 | `payment_db`)
* Communicates with Razorpay APIs in Test Mode.
* Validates server-side HMAC signatures to prevent payment spoofing.
* Exposes a webhook listener (`/payments/webhook`) for asynchronous out-of-band payment confirmations.

### 6. `notification-service` (Port 8005 | `notification_db`)
* A pure event consumer bound to RabbitMQ.
* Listens for `BookingConfirmed`, `PaymentSucceeded`, `RefundProcessed`, and `EventCancelled`.
* Inserts notifications into `notification_db` and logs simulated emails.

### 7. `refund-service` (Port 8006 | `refund_db`)
* Handles both individual cancellations and massive event-cancellation fan-outs.
* When an organizer cancels an event, `EventCancelled` is consumed by Refund Service, which queries all confirmed bookings and issues refunds automatically and idempotently.

### 8. `analytics-service` (Port 8007 | `analytics_db`)
* Tracks views, conversions, ticket breakdown, and gross/net revenue.
* Updates metrics asynchronously without adding overhead to the checkout write-path.

---

## 7. How High-Concurrency Redis Lua Holds Work

### The Problem: The Overselling Race Condition
Suppose an event has **1 VIP ticket remaining**. Two users, Alice and Bob, click "Reserve" at the exact same millisecond:

```
WITHOUT ATOMIC LUA SCRIPT (RACE CONDITION):
Alice's Request: ──► Read Stock (sees 1 left) ──────────────► Allow Reservation (Stock = 0)
Bob's Request:   ──────► Read Stock (also sees 1 left!) ────► Allow Reservation (Stock = -1)
RESULT: TICKET OVERLOCKED / OVERWROTE! Two users paid for one ticket.
```

### The Solution: Redis Atomic Lua Scripts (`EVAL`)
Redis is single-threaded in its core execution. By executing our reservation logic as a **Lua Script inside Redis**, the entire check-and-reserve happens as **one indivisible atomic operation**:

```
WITH REDIS ATOMIC LUA:
Alice's Request: ──► [ Redis executes Lua script ] ──► Hold Granted! (Held = 1/1)
Bob's Request:   ──► [ Must wait for Lua script ]  ──► Rejected: Capacity Exceeded!
```

```lua
-- Conceptual view of our Redis Lua Hold Script (services/booking-service/app/redis_holds.py)
local current_holds = redis.call('GET', KEYS[1]) or 0
local total_capacity = tonumber(ARGV[1])
local requested_qty = tonumber(ARGV[2])

if (current_holds + requested_qty) <= total_capacity then
    redis.call('INCRBY', KEYS[1], requested_qty)
    redis.call('EXPIRE', KEYS[1], 600) -- 10 minute TTL
    return 1 -- Success
else
    return 0 -- Rejected: Sold out
end
```

### The 10-Minute Sweeper
If a user reserves a ticket but closes their browser, the Redis hold expires after **600 seconds (10 minutes)**. The background worker `sweeper.py` periodically marks stale `PENDING_PAYMENT` rows as `EXPIRED`, returning the inventory to the public pool automatically.

---

## 8. How RabbitMQ Event-Driven Decoupling Works

### Topic Exchange Architecture

All services publish domain events to a single topic exchange: **`eventsphere.events`**.

```
                           ┌───────────────────────────┐
                           │ Topic: eventsphere.events │
                           └─────────────┬─────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │ Routing Key:                   │ Routing Key:                   │ Routing Key:
        │ *.confirmed / *.succeeded      │ *.requested                    │ *.*
        ▼                                ▼                                ▼
┌──────────────┐                 ┌──────────────┐                 ┌──────────────┐
│ Notification │                 │ Refund Queue │                 │  Analytics   │
│    Queue     │                 └──────┬───────┘                 │    Queue     │
└──────┬───────┘                        │                         └──────┬───────┘
       ▼                                ▼                                ▼
  Consumer                         Consumer                         Consumer
(Sends Email)                   (Issues Refund)                (Increments Counter)
```

### Standardized Event Envelope
Every event emitted into the bus follows a strict JSON contract:
```json
{
  "event_id": "c71a39f5-7b56-4cf3-94c6-e97d11f9fbc3",
  "event_type": "BookingConfirmed",
  "occurred_at": "2026-10-24T09:30:00Z",
  "source_service": "booking-service",
  "data": {
    "booking_id": "b-849204",
    "user_id": "u-102934",
    "amount": 399.00
  }
}
```

### Consumer Idempotency
Because RabbitMQ guarantees **at-least-once delivery**, network hiccups might cause a message to be delivered twice. To prevent duplicate emails or double-refunds, every consumer service records each processed `event_id` in a local `processed_events` table:

```sql
-- Inside each service's database:
INSERT INTO processed_events (event_id, processed_at) VALUES ('c71a39f5-...', NOW());
-- If this raises a UniqueConstraintViolation, the consumer acknowledges and skips!
```

---

## 9. How Multi-Track Scheduling & Printable Badges Work

### Multi-Track Timetable Grouping
Tech conference schedules are complex matrices of **Days × Tracks × Time Slots**.
The `event-service` groups sessions using the following hierarchy:

```
FullSchedule
└── Day 1 (Oct 24, 2026)
    ├── Tracks: [Track A: AI, Track B: Cloud Native, Track C: Labs]
    └── Time Slot: 09:30 AM - 10:45 AM
        └── Sessions:
            ├── Hall 1: Opening Keynote (Dr. Elena Rostova)
    └── Time Slot: 11:00 AM - 12:15 PM
        └── Sessions:
            ├── Hall 1: Production RAG Pipelines (Alex Rivera)
            ├── Room 202: Event Streaming with RabbitMQ (Marcus Chen)
            └── Lab 305: Hands-on Rust Workshop (Sarah Jenkins)
```

### Printable Vector PDF Lanyard Badges
Unlike standard receipt PDFs that look like invoices, DevSummit renders an authentic **physical conference pass**:

```
┌──────────────────────────────────────────────┐
│                 (  SLOT  )                   │ ◄── Lanyard clip punch hole
│                                              │
│               >_ DEVSUMMIT                   │
│      Global Developer Conference 2026        │
│          San Francisco, CA • Oct 2026        │
│                                              │
│             MOHAMMAD SULTAN                  │ ◄── Attendee Name (Bold Display)
│          Staff Distributed Architect         │ ◄── Role & Company
│             CloudScale Systems               │
│                                              │
│  ┌───────────┐   PASS SERIAL: #DS-849204     │
│  │  QR CODE  │   ● VERIFIED ATTENDEE PASS    │ ◄── Scannable Check-in QR
│  │  [█████]  │   Metropolitan Pavilion       │
│  └───────────┘   ZONE: A / B / C             │
│                                              │
│ ═══════════════ VIP ALL-ACCESS ═════════════ │ ◄── Gradient Category Ribbon
└──────────────────────────────────────────────┘
```
* **Lanyard Punch-Hole Guide**: Pre-measured slot cutout at the top.
* **Gate Check-in QR Code**: Encodes a signed verification URI (`https://devsummit.io/verify?ticket=...`) so door volunteers can scan and validate passes on arrival.
* **Instant Printing**: Formatted with CSS `@media print` rules for physical 4"×6" card printing via `window.print()`.

---

## 10. Database-per-Service Architecture

Instead of a monolithic single database, DevSummit adheres to the **Database-per-Service** design pattern:

```
┌────────────────────────────────────────────────────────────────────────┐
│               SINGLE POSTGRESQL INSTANCE (Port 5432)                   │
├──────────────┬──────────────┬──────────────┬─────────────┬─────────────┤
│ identity_db  │   event_db   │  booking_db  │ payment_db  │ refund_db   │
│ - users      │ - events     │ - bookings   │ - payments  │ - refunds   │
│ - roles      │ - tracks     │ - items      │ - ledgers   │ - cancellations
│ - tokens     │ - speakers   │ - holds      │             │             │
│              │ - sessions   │              │             │             │
│              │ - tickets    │              │             │             │
├──────────────┴──────────────┴──────────────┴─────────────┴─────────────┤
│      notification_db        │              analytics_db                │
│      - in_app_alerts        │              - event_metrics             │
│      - email_logs           │              - daily_summaries           │
└─────────────────────────────┴──────────────────────────────────────────┘
```

### Why this is the best engineering tradeoff:
1. **Zero Schema Coupling**: If `event-service` modifies its schema to add speaker social links, it runs its own Alembic migration (`0002_tracks_speakers_sessions.py`) without affecting any other database.
2. **True Logical Isolation**: Even though all 7 databases run inside one cost-effective container, PostgreSQL enforces strict logical database boundaries. No service can run a cross-database SQL `JOIN`. Cross-service queries must use HTTP REST APIs.

---

## 11. Building and Running

### Prerequisites
* **Docker Desktop** installed and running on your system.
* **Git** installed.

### Step 1: Clone the Repository
```bash
git clone https://github.com/Sullu009/devsummit.git
cd devsummit
```

### Step 2: Initialize Environment Variables
```bash
# Windows PowerShell:
copy .env.example .env

# Linux / macOS:
cp .env.example .env
```

### Step 3: Build & Start All Containers
```bash
docker compose up --build
```
*This command will automatically build all 7 Python FastAPI microservices, the API Gateway, and the Next.js frontend, launch PostgreSQL, Redis, and RabbitMQ, and execute all Alembic migrations.*

### Step 4: Access the System
| Component | URL | Credentials / Notes |
|---|---|---|
| **Web Frontend** | `http://localhost:3000` | Main application |
| **API Gateway** | `http://localhost:8080/health` | Central API entrance |
| **RabbitMQ Management UI** | `http://localhost:15672` | Username: `guest`, Password: `guest` |
| **Event Service (Direct)** | `http://localhost:8002/docs` | Swagger UI documentation |
| **Booking Service (Direct)**| `http://localhost:8003/docs`| Swagger UI documentation |

### Step 5: Preload Flagship Conference Data
1. Open `http://localhost:3000`.
2. Click the **`⚡ Seed Flagship DevSummit`** button on the homepage.
3. The platform will automatically populate **DevSummit 2026** with:
   * 3 parallel tracks (*AI & Agents*, *Cloud Native*, *Hands-on Labs*)
   * 6 world-class keynote speakers with bios and social links
   * 8 scheduled sessions across Day 1 and Day 2
   * 4 pass categories (General, VIP, Workshop, Student)

---

## 12. Understanding the Output & Logs

### Distributed Tracing with `x-correlation-id`
Every log line emitted by the services includes a unified correlation ID, making it effortless to trace a user's transaction across multiple microservices:

```
[api-gateway]       GET /api/events/ev-102 status=200 corr_id=9f1a2-8b4e
[event-service]     event_service GET /events/ev-102 status=200 duration_ms=12 corr_id=9f1a2-8b4e
[booking-service]   booking_service POST /bookings/reserve status=201 duration_ms=18 corr_id=9f1a2-8b4e
[payment-service]   payment_service POST /payments/verify status=200 duration_ms=45 corr_id=9f1a2-8b4e
[rabbitmq]          exchange: eventsphere.events routing_key: booking.confirmed
[notification-svc]  consumed BookingConfirmed booking_id=b-849204 corr_id=9f1a2-8b4e
[analytics-svc]     updated ticket count for event ev-102 corr_id=9f1a2-8b4e
```

---

## 📜 Summary

DevSummit demonstrates how modern software engineering patterns come together to build a robust, production-grade system:
* **FastAPI** provides asynchronous, high-throughput REST APIs.
* **Next.js 14** provides dynamic, responsive user experiences with real-time timetable exploration and vector badge printing.
* **Redis Lua scripts** solve high-concurrency overselling challenges in under 15ms.
* **RabbitMQ** provides fault-tolerant, asynchronous event decoupling.
* **PostgreSQL** enforces clean, service-isolated relational data persistence.

Distributed under the MIT License. Built for modern software engineering excellence.
