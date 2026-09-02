"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { EventDetail } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function EditEventPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [event, setEvent] = useState<EventDetail | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<EventDetail>(`/events/${id}`).then((e) => {
      setEvent(e);
      setTitle(e.title);
      setDescription(e.description);
    });
  }, [id]);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const updated = await api.patch<EventDetail>(`/events/${id}`, { title, description });
      setEvent(updated);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save changes.");
    } finally {
      setSaving(false);
    }
  }

  async function publish() {
    try {
      const updated = await api.post<EventDetail>(`/events/${id}/publish`);
      setEvent(updated);
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not publish.");
    }
  }

  if (!event) return <div className="mx-auto max-w-2xl px-6 py-20 text-muted text-sm">Loading…</div>;

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-3xl">{event.title}</h1>
        <StatusPill status={event.status} />
      </div>

      <div className="flex gap-4 text-sm mb-8">
        <Link href={`/organizer/events/${id}/bookings`} className="hairline px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors">
          Bookings
        </Link>
        <Link href={`/organizer/events/${id}/analytics`} className="hairline px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors">
          Analytics
        </Link>
        <Link href={`/organizer/events/${id}/payments`} className="hairline px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors">
          Payments &amp; revenue
        </Link>
        {event.status === "DRAFT" && (
          <button onClick={publish} className="bg-ink text-paper px-3 py-1.5 hover:bg-forest transition-colors">
            Publish event
          </button>
        )}
      </div>

      <form onSubmit={save} className="space-y-4">
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Title</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Description</label>
          <textarea rows={5} value={description} onChange={(e) => setDescription(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-muted mb-2">Ticket types</p>
          <div className="space-y-px bg-line hairline">
            {event.ticket_types.map((tt) => (
              <div key={tt.id} className="bg-paper p-3 flex justify-between text-sm">
                <span>{tt.name}</span>
                <span className="font-mono text-muted">
                  ₹{Number(tt.price).toLocaleString("en-IN")} · {tt.quantity_available}/{tt.quantity_total} left
                </span>
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-rust text-sm">{error}</p>}

        <button type="submit" disabled={saving} className="hairline px-5 py-2.5 text-sm hover:bg-ink hover:text-paper transition-colors disabled:opacity-50">
          {saving ? "Saving…" : "Save changes"}
        </button>
      </form>
    </div>
  );
}
