"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import type { EventSummary, PaginatedEvents } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function OrganizerEventsPage() {
  const [events, setEvents] = useState<EventSummary[] | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(() => {
    api.get<PaginatedEvents>("/events?mine=true&page_size=100").then((r) => setEvents(r.items));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function publish(id: string) {
    setBusyId(id);
    try {
      await api.post(`/events/${id}/publish`);
      load();
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not publish event.");
    } finally {
      setBusyId(null);
    }
  }

  async function cancel(id: string) {
    if (!confirm("Cancel this event? All confirmed attendees will be automatically refunded.")) return;
    setBusyId(id);
    try {
      await api.post(`/events/${id}/cancel`);
      load();
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not cancel event.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-display text-3xl">Your events</h1>
        <Link href="/organizer/events/new" className="bg-ink text-paper px-5 py-3 text-sm hover:bg-forest transition-colors">
          + New event
        </Link>
      </div>

      <div className="space-y-px bg-line hairline">
        {events?.map((e) => (
          <div key={e.id} className="bg-paper p-4 flex items-center justify-between">
            <Link href={`/organizer/events/${e.id}/edit`} className="flex-1">
              <p className="text-sm font-medium">{e.title}</p>
              <p className="text-xs text-muted mt-0.5">{new Date(e.starts_at).toLocaleDateString()}</p>
            </Link>
            <div className="flex items-center gap-4">
              <StatusPill status={e.status} />
              <Link href={`/organizer/events/${e.id}/bookings`} className="text-xs text-muted hover:text-ink">
                Bookings
              </Link>
              <Link href={`/organizer/events/${e.id}/analytics`} className="text-xs text-muted hover:text-ink">
                Analytics
              </Link>
              <Link href={`/organizer/events/${e.id}/payments`} className="text-xs text-muted hover:text-ink">
                Payments
              </Link>
              {e.status === "DRAFT" && (
                <button onClick={() => publish(e.id)} disabled={busyId === e.id} className="hairline px-3 py-1.5 text-xs hover:bg-ink hover:text-paper transition-colors">
                  Publish
                </button>
              )}
              {e.status !== "CANCELLED" && (
                <button onClick={() => cancel(e.id)} disabled={busyId === e.id} className="hairline px-3 py-1.5 text-xs hover:bg-rust hover:text-paper hover:border-rust transition-colors">
                  Cancel
                </button>
              )}
            </div>
          </div>
        ))}
        {events && events.length === 0 && <p className="bg-paper p-5 text-sm text-muted">No events yet.</p>}
      </div>
    </div>
  );
}
