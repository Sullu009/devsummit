"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import type { PaginatedEvents } from "@/lib/types";
import { EventCard } from "@/components/event-card";

export default function HomePage() {
  const [events, setEvents] = useState<PaginatedEvents | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [seeding, setSeeding] = useState(false);
  const [seedSuccess, setSeedSuccess] = useState<string | null>(null);

  function loadEvents() {
    api
      .get<PaginatedEvents>("/events?page=1&page_size=6")
      .then(setEvents)
      .catch((e) => setError(e.message));
  }

  useEffect(() => {
    loadEvents();
  }, []);

  async function handleSeedDemo() {
    setSeeding(true);
    setSeedSuccess(null);
    try {
      await api.post("/events/seed-demo", {});
      setSeedSuccess("DevSummit 2026 conference seeded with tracks, speakers & schedule!");
      loadEvents();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to seed conference data.");
    } finally {
      setSeeding(false);
    }
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 pt-16 pb-14 border-b border-line">
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <span className="font-mono text-xs uppercase tracking-widest text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded font-bold">
            &gt;_ Tech Conferences &amp; Developer Workshops
          </span>
          <span className="font-mono text-xs text-muted">
            • Multi-Track Agenda • Digital Lanyard Badges
          </span>
        </div>

        <h1 className="font-display text-5xl md:text-6xl font-extrabold tracking-tight leading-[1.05] max-w-3xl text-ink">
          Where engineering leaders, researchers, and builders converge.
        </h1>

        <p className="text-muted mt-5 max-w-xl text-lg leading-relaxed">
          Discover world-class developer summits, navigate concurrent multi-track agendas, explore talk abstracts from top engineers, and download official lanyard badges.
        </p>

        <div className="mt-8 flex flex-wrap items-center gap-3">
          <Link href="/events" className="bg-ink text-paper px-6 py-3 text-sm font-semibold hover:bg-indigo-700 transition-colors shadow-sm">
            Explore Conferences &amp; Labs
          </Link>
          <Link href="/register" className="hairline px-5 py-3 text-sm font-semibold hover:bg-paper transition-colors">
            Organizer Portal
          </Link>
          <button
            onClick={handleSeedDemo}
            disabled={seeding}
            className="hairline px-4 py-3 text-xs font-mono text-indigo-700 bg-indigo-50/70 hover:bg-indigo-100 transition-colors disabled:opacity-50"
            title="Preload flagship DevSummit with 3 tracks, 6 speakers, and multi-day timetable"
          >
            {seeding ? "Bootstrapping..." : "⚡ Seed Flagship DevSummit"}
          </button>
        </div>

        {seedSuccess && (
          <p className="mt-3 text-xs text-emerald-700 font-mono bg-emerald-50 px-3 py-1.5 rounded inline-block">
            ✓ {seedSuccess}
          </p>
        )}
      </section>

      {/* Feature Highlights Grid */}
      <section className="mx-auto max-w-6xl px-6 py-10 border-b border-line">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="hairline p-5 bg-surface">
            <span className="text-xl">🗺️</span>
            <h3 className="font-display text-base font-bold mt-2">Multi-Track Timetables</h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              Navigate concurrent tracks (AI, Cloud Native, Rust) with room locations and interactive session abstracts.
            </p>
          </div>
          <div className="hairline p-5 bg-surface">
            <span className="text-xl">🎤</span>
            <h3 className="font-display text-base font-bold mt-2">Verified Speaker Profiles</h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              Browse keynotes from industry pioneers, view talk abstracts, and connect via GitHub and LinkedIn.
            </p>
          </div>
          <div className="hairline p-5 bg-surface">
            <span className="text-xl">📇</span>
            <h3 className="font-display text-base font-bold mt-2">Printable Lanyard Badges</h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              Instant vector PDF conference badges with QR code gate check-in and custom attendee designations.
            </p>
          </div>
        </div>
      </section>

      {/* Featured Conferences Section */}
      <section className="mx-auto max-w-6xl px-6 py-14">
        <div className="flex items-baseline justify-between mb-6">
          <div>
            <h2 className="font-display text-2xl font-bold">Upcoming Tech Summits</h2>
            <p className="text-xs text-muted mt-0.5">Reserve passes with real-time Redis concurrency protection</p>
          </div>
          <Link href="/events" className="text-sm font-semibold text-indigo-700 hover:underline">
            View all →
          </Link>
        </div>

        {error && <p className="text-rust text-sm">Could not load events: {error}</p>}
        {!events && !error && <p className="text-muted text-sm">Loading summits…</p>}
        {events && events.items.length === 0 && (
          <div className="hairline p-8 text-center bg-surface">
            <p className="text-muted text-sm">No published conferences found in the database yet.</p>
            <button
              onClick={handleSeedDemo}
              disabled={seeding}
              className="mt-3 bg-ink text-paper px-4 py-2 text-xs font-mono font-medium hover:bg-indigo-700 transition-colors"
            >
              Click here to seed DevSummit 2026 data
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-px bg-line hairline">
          {events?.items.map((e) => (
            <div key={e.id} className="bg-paper">
              <EventCard event={e} />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
