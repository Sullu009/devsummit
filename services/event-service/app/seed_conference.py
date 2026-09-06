"""Seed script for DevSummit tech conference data."""

import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import (
    Event,
    EventCategory,
    EventStatus,
    Session as SessionModel,
    Speaker,
    TicketType,
    Track,
)

logger = logging.getLogger("devsummit.seed")


def seed_conference_data(db: Session, organizer_id: str = "org-devsummit-001") -> Event:
    """Idempotently seeds the flagship DevSummit conference."""
    # Check if already exists
    existing = db.execute(select(Event).where(Event.slug.like("devsummit-2026%"))).scalars().first()
    if existing:
        logger.info("DevSummit conference already seeded: %s", existing.id)
        return existing

    base_time = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=30)
    day1_start = base_time
    day2_end = base_time + timedelta(days=1, hours=9)

    event = Event(
        organizer_id=organizer_id,
        title="DevSummit 2026: Global Developer & AI Conference",
        slug=f"devsummit-2026-global-{base_time.strftime('%Y%m')}",
        description=(
            "DevSummit 2026 brings together 2,500+ software architects, engineers, and researchers "
            "for 2 packed days of cutting-edge keynotes, multi-track deep dives into Generative AI, "
            "distributed systems, high-concurrency microservices, and interactive hands-on coding workshops."
        ),
        category=EventCategory.TECH,
        status=EventStatus.PUBLISHED,
        cover_image_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?auto=format&fit=crop&w=1600&q=80",
        venue_name="Metropolitan Tech Pavilion & Convention Center",
        venue_address="742 Innovation Way, SOMA District",
        city="San Francisco, CA",
        starts_at=day1_start,
        ends_at=day2_end,
    )

    # 1. Ticket Types
    event.ticket_types = [
        TicketType(
            name="General Attendee Pass",
            description="Access to all keynotes and Track A & B sessions, conference lunch, and attendee swag bag.",
            price=Decimal("199.00"),
            quantity_total=1200,
            quantity_available=1200,
            sale_starts_at=day1_start - timedelta(days=60),
            sale_ends_at=day1_start - timedelta(hours=2),
        ),
        TicketType(
            name="VIP All-Access Pass",
            description="All keynotes & tracks, reserved front-row seating, VIP lounge catering, and invitation to the Speaker Dinner.",
            price=Decimal("399.00"),
            quantity_total=250,
            quantity_available=250,
            sale_starts_at=day1_start - timedelta(days=60),
            sale_ends_at=day1_start - timedelta(hours=2),
        ),
        TicketType(
            name="Hands-on Workshop Pass",
            description="Full-day intensive bring-your-own-laptop interactive labs in Track C with direct mentor feedback.",
            price=Decimal("299.00"),
            quantity_total=300,
            quantity_available=300,
            sale_starts_at=day1_start - timedelta(days=60),
            sale_ends_at=day1_start - timedelta(hours=2),
        ),
        TicketType(
            name="Student / Academic Pass",
            description="Subsidized full conference pass for enrolled undergraduate and graduate students.",
            price=Decimal("49.00"),
            quantity_total=200,
            quantity_available=200,
            sale_starts_at=day1_start - timedelta(days=60),
            sale_ends_at=day1_start - timedelta(hours=2),
        ),
    ]

    # 2. Tracks
    track_ai = Track(
        name="Track A: Generative AI & Autonomous Agents",
        description="Autonomous multi-agent swarms, LLM fine-tuning, RAG architectures, and production neural search.",
        room_location="Main Auditorium (Hall 1)",
        color_code="#6366F1",
        order=1,
    )
    track_dist = Track(
        name="Track B: Distributed Systems & Cloud Native",
        description="High-throughput microservices, event-driven messaging, consensus protocols, and Kubernetes at scale.",
        room_location="Innovation Hall (Room 202)",
        color_code="#06B6D4",
        order=2,
    )
    track_labs = Track(
        name="Track C: Hands-on Workshops & Deep Dives",
        description="Interactive coding laboratories with live debugging, load testing, and architectural refactoring.",
        room_location="Hacker Lab (Room 305)",
        color_code="#10B981",
        order=3,
    )
    event.tracks = [track_ai, track_dist, track_labs]

    # 3. Speakers
    spk_elena = Speaker(
        name="Dr. Elena Rostova",
        role_title="VP of AI Systems",
        company="DeepMind Labs",
        bio="Author of 'Autonomous Agent Architectures'. Elena leads foundation model research focused on multi-agent collaboration and reasoning trees.",
        avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/erostova",
        twitter_url="https://x.com/elena_ai",
        linkedin_url="https://linkedin.com/in/elena-rostova",
    )
    spk_marcus = Speaker(
        name="Marcus Chen",
        role_title="Principal Distributed Systems Architect",
        company="CloudScale Global",
        bio="Veteran engineer responsible for scaling event streaming pipelines to over 10 million messages per second across multi-region clusters.",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/marcuschen",
        twitter_url="https://x.com/marcus_dist",
        linkedin_url="https://linkedin.com/in/marcus-chen-dist",
    )
    spk_sarah = Speaker(
        name="Sarah Jenkins",
        role_title="Core Maintainer & Systems Engineer",
        company="Rust Foundation & HyperFlow",
        bio="Creator of popular asynchronous network runtimes and passionate advocate for memory-safe, zero-overhead systems programming.",
        avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/sjenkins-dev",
        twitter_url="https://x.com/sarah_rust",
        linkedin_url="https://linkedin.com/in/sarah-jenkins-dev",
    )
    spk_alex = Speaker(
        name="Alex Rivera",
        role_title="Staff AI Infrastructure Engineer",
        company="Anthropic Systems",
        bio="Alex specializes in low-latency vector databases, caching tiers, and context window optimization for production enterprise copilots.",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/arivera-ai",
        twitter_url="https://x.com/alexrivera",
        linkedin_url="https://linkedin.com/in/alex-rivera-systems",
    )
    spk_priya = Speaker(
        name="Priya Sharma",
        role_title="Head of Database Reliability",
        company="NexaFin Tech",
        bio="Priya designs zero-downtime data migration strategies and active-active replication models for mission-critical financial applications.",
        avatar_url="https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/psharma-db",
        twitter_url="https://x.com/priyasharma_db",
        linkedin_url="https://linkedin.com/in/priya-sharma-db",
    )
    spk_david = Speaker(
        name="David Thorne",
        role_title="Lead Container Engineer",
        company="KubeForge Technologies",
        bio="Maintainer of multiple CNCF cloud-native tools, focused on eBPF telemetry, service meshes, and custom Kubernetes operator development.",
        avatar_url="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80",
        github_url="https://github.com/dthorne-kube",
        twitter_url="https://x.com/david_k8s",
        linkedin_url="https://linkedin.com/in/davidthorne-k8s",
    )
    event.speakers = [spk_elena, spk_marcus, spk_sarah, spk_alex, spk_priya, spk_david]

    # 4. Sessions - Day 1
    # 09:30 - 10:45 Keynote (All Tracks attend)
    s1 = SessionModel(
        title="Opening Keynote: The Dawn of Autonomous Cognitive Systems",
        abstract=(
            "An eye-opening kickoff exploring how foundation models are transitioning from passive chat interfaces "
            "to self-orchestrating multi-agent networks that plan, write code, verify logic, and deploy resilient services."
        ),
        session_type="KEYNOTE",
        start_time=day1_start + timedelta(minutes=30),
        end_time=day1_start + timedelta(hours=1, minutes=45),
        track=track_ai,
        speaker=spk_elena,
    )

    # 11:00 - 12:15 Parallel Sessions
    s2 = SessionModel(
        title="Building Production-Grade RAG: Beyond Naive Vector Search",
        abstract=(
            "Deep dive into semantic chunking, reciprocal rank fusion (RRF), re-ranking models, and Redis caching layers "
            "to build retrieval-augmented generation pipelines that never hallucinate and execute in under 120ms."
        ),
        session_type="TALK",
        start_time=day1_start + timedelta(hours=2),
        end_time=day1_start + timedelta(hours=3, minutes=15),
        track=track_ai,
        speaker=spk_alex,
    )
    s3 = SessionModel(
        title="Architecting Resilient Event Streams with RabbitMQ & Outbox Pattern",
        abstract=(
            "Learn how to eliminate split-brain states and dual-write data inconsistencies between microservices "
            "using transactional outbox patterns, idempotent consumers, and backpressure monitoring."
        ),
        session_type="TALK",
        start_time=day1_start + timedelta(hours=2),
        end_time=day1_start + timedelta(hours=3, minutes=15),
        track=track_dist,
        speaker=spk_marcus,
    )
    s4 = SessionModel(
        title="Workshop Lab: Writing High-Performance Rust Microservices from Scratch",
        abstract=(
            "Bring your laptop! In this 3-hour hands-on lab, we will build an asynchronous HTTP service using Axum/Tokio, "
            "implement connection pooling, and benchmark throughput against equivalent Node.js and Go services."
        ),
        session_type="WORKSHOP",
        start_time=day1_start + timedelta(hours=2),
        end_time=day1_start + timedelta(hours=5),
        track=track_labs,
        speaker=spk_sarah,
    )

    # 14:00 - 15:15 Parallel Sessions
    s5 = SessionModel(
        title="Zero-Downtime PostgreSQL Migrations for Sharded Microservices",
        abstract=(
            "Field-tested patterns for online schema migrations, column deprecation, lock management, "
            "and replica synchronization in high-concurrency relational architectures."
        ),
        session_type="TALK",
        start_time=day1_start + timedelta(hours=5),
        end_time=day1_start + timedelta(hours=6, minutes=15),
        track=track_dist,
        speaker=spk_priya,
    )
    s6 = SessionModel(
        title="eBPF in Action: Kernel-Level Observability & Security Monitoring",
        abstract=(
            "Discover how eBPF programs let you trace every network packet, system call, and file access directly in the Linux kernel "
            "with sub-microsecond overhead and zero application code modification."
        ),
        session_type="TALK",
        start_time=day1_start + timedelta(hours=5),
        end_time=day1_start + timedelta(hours=6, minutes=15),
        track=track_dist,
        speaker=spk_david,
    )

    # Day 2 Sessions
    day2_start = day1_start + timedelta(days=1)
    s7 = SessionModel(
        title="Day 2 Keynote: The Future of Systems Engineering in the AI Era",
        abstract=(
            "A candid exploration of how compiler toolchains, formal verification, and distributed consensus "
            "protocols are adapting to accommodate non-deterministic AI compute graphs."
        ),
        session_type="KEYNOTE",
        start_time=day2_start + timedelta(minutes=30),
        end_time=day2_start + timedelta(hours=1, minutes=45),
        track=track_ai,
        speaker=spk_sarah,
    )
    s8 = SessionModel(
        title="Workshop Lab: Building & Deploying Multi-Agent Systems with Guardrails",
        abstract=(
            "Hands-on workshop configuring agent hierarchies, tool dispatching, loop prevention, and schema enforcement "
            "using open standards and local LLMs."
        ),
        session_type="WORKSHOP",
        start_time=day2_start + timedelta(hours=2),
        end_time=day2_start + timedelta(hours=5),
        track=track_labs,
        speaker=spk_elena,
    )

    event.sessions = [s1, s2, s3, s4, s5, s6, s7, s8]

    db.add(event)
    db.commit()
    db.refresh(event)
    logger.info("Successfully seeded DevSummit conference with ID: %s", event.id)
    return event
