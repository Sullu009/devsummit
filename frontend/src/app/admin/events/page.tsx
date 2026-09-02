"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { EventSummary, PaginatedEvents } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function AdminEventsPage() {
  const [events, setEvents] = useState<EventSummary[] | null>(null);

  const load = useCallback(() => {
    api.get<PaginatedEvents>("/events?admin_all=true&page_size=200").then((r) => setEvents(r.items));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function cancelEvent(id: string) {
    if (!confirm("Cancel this event as an admin?")) return;
    await api.post(`/events/${id}/cancel`);
    load();
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">All events</h1>
      <div className="space-y-px bg-line hairline">
        {events?.map((e) => (
          <div key={e.id} className="bg-paper p-4 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">{e.title}</p>
              <p className="text-xs text-muted mt-0.5">{e.city} · {new Date(e.starts_at).toLocaleDateString()}</p>
            </div>
            <div className="flex items-center gap-4">
              <StatusPill status={e.status} />
              {e.status !== "CANCELLED" && (
                <button onClick={() => cancelEvent(e.id)} className="hairline px-3 py-1.5 text-xs hover:bg-rust hover:text-paper hover:border-rust transition-colors">
                  Cancel
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
