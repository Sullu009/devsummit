"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { EventSummary, PaginatedEvents } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function OrganizerDashboardPage() {
  const { user } = useAuth();
  const [events, setEvents] = useState<EventSummary[] | null>(null);

  useEffect(() => {
    api.get<PaginatedEvents>("/events?mine=true&page_size=50").then((r) => setEvents(r.items));
  }, []);

  const published = events?.filter((e) => e.status === "PUBLISHED").length ?? 0;
  const drafts = events?.filter((e) => e.status === "DRAFT").length ?? 0;

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl">Organizer dashboard</h1>
          <p className="text-muted text-sm mt-1">Welcome back, {user?.full_name}.</p>
        </div>
        <Link href="/organizer/events/new" className="bg-ink text-paper px-5 py-3 text-sm hover:bg-forest transition-colors">
          + New event
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-px bg-line hairline mb-10">
        <div className="bg-paper p-5">
          <p className="text-xs uppercase tracking-wide text-muted">Total events</p>
          <p className="font-display text-3xl mt-1">{events?.length ?? "—"}</p>
        </div>
        <div className="bg-paper p-5">
          <p className="text-xs uppercase tracking-wide text-muted">Published</p>
          <p className="font-display text-3xl mt-1">{published}</p>
        </div>
        <div className="bg-paper p-5">
          <p className="text-xs uppercase tracking-wide text-muted">Drafts</p>
          <p className="font-display text-3xl mt-1">{drafts}</p>
        </div>
      </div>

      <div className="flex items-baseline justify-between mb-4">
        <h2 className="font-display text-xl">Your events</h2>
        <Link href="/organizer/events" className="text-sm text-forest hover:underline">
          View all →
        </Link>
      </div>

      <div className="space-y-px bg-line hairline">
        {events?.slice(0, 8).map((e) => (
          <Link key={e.id} href={`/organizer/events/${e.id}/edit`} className="bg-paper p-4 flex items-center justify-between block hover:bg-line/10">
            <div>
              <p className="text-sm font-medium">{e.title}</p>
              <p className="text-xs text-muted mt-0.5">{new Date(e.starts_at).toLocaleDateString()} · {e.city || "No location"}</p>
            </div>
            <StatusPill status={e.status} />
          </Link>
        ))}
        {events && events.length === 0 && <p className="bg-paper p-5 text-sm text-muted">No events yet. Create your first one.</p>}
      </div>
    </div>
  );
}
