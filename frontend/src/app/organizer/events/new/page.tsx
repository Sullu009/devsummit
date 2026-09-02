"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import type { EventCategory, EventDetail } from "@/lib/types";

interface TicketDraft {
  name: string;
  price: string;
  quantity_total: string;
}

const CATEGORIES: EventCategory[] = ["MUSIC", "TECH", "BUSINESS", "ARTS", "SPORTS", "FOOD", "COMMUNITY", "OTHER"];

function toIso(dateStr: string): string {
  return new Date(dateStr).toISOString();
}

export default function NewEventPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState<EventCategory>("TECH");
  const [venueName, setVenueName] = useState("");
  const [venueAddress, setVenueAddress] = useState("");
  const [city, setCity] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [tickets, setTickets] = useState<TicketDraft[]>([{ name: "General Admission", price: "499", quantity_total: "100" }]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function updateTicket(i: number, field: keyof TicketDraft, value: string) {
    setTickets((t) => t.map((tk, idx) => (idx === i ? { ...tk, [field]: value } : tk)));
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const saleStart = new Date().toISOString();
      const event = await api.post<EventDetail>("/events", {
        title,
        description,
        category,
        venue_name: venueName,
        venue_address: venueAddress,
        city,
        starts_at: toIso(startsAt),
        ends_at: toIso(endsAt),
        ticket_types: tickets
          .filter((t) => t.name && t.price && t.quantity_total)
          .map((t) => ({
            name: t.name,
            description: "",
            price: t.price,
            quantity_total: parseInt(t.quantity_total, 10),
            sale_starts_at: saleStart,
            sale_ends_at: toIso(startsAt),
          })),
      });
      router.push(`/organizer/events/${event.id}/edit`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create event.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">Create an event</h1>

      <form onSubmit={onSubmit} className="space-y-6">
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Title</label>
          <input required value={title} onChange={(e) => setTitle(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>

        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Description</label>
          <textarea rows={4} value={description} onChange={(e) => setDescription(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>

        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Category</label>
          <select value={category} onChange={(e) => setCategory(e.target.value as EventCategory)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink">
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Venue name</label>
            <input value={venueName} onChange={(e) => setVenueName(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">City</label>
            <input value={city} onChange={(e) => setCity(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
          </div>
        </div>
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Address</label>
          <input value={venueAddress} onChange={(e) => setVenueAddress(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Starts at</label>
            <input required type="datetime-local" value={startsAt} onChange={(e) => setStartsAt(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
          </div>
          <div>
            <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Ends at</label>
            <input required type="datetime-local" value={endsAt} onChange={(e) => setEndsAt(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs uppercase tracking-wide text-muted">Ticket types</label>
            <button
              type="button"
              onClick={() => setTickets((t) => [...t, { name: "", price: "", quantity_total: "" }])}
              className="text-xs text-forest hover:underline"
            >
              + Add ticket type
            </button>
          </div>
          <div className="space-y-2">
            {tickets.map((t, i) => (
              <div key={i} className="grid grid-cols-3 gap-2">
                <input placeholder="Name" value={t.name} onChange={(e) => updateTicket(i, "name", e.target.value)} className="hairline px-3 py-2 bg-surface text-sm focus:outline-none focus:border-ink" />
                <input placeholder="Price ₹" type="number" min="0" value={t.price} onChange={(e) => updateTicket(i, "price", e.target.value)} className="hairline px-3 py-2 bg-surface text-sm focus:outline-none focus:border-ink" />
                <input placeholder="Quantity" type="number" min="1" value={t.quantity_total} onChange={(e) => updateTicket(i, "quantity_total", e.target.value)} className="hairline px-3 py-2 bg-surface text-sm focus:outline-none focus:border-ink" />
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-rust text-sm">{error}</p>}

        <button type="submit" disabled={submitting} className="bg-ink text-paper px-5 py-3 text-sm hover:bg-forest transition-colors disabled:opacity-50">
          {submitting ? "Creating…" : "Save as draft"}
        </button>
      </form>
    </div>
  );
}
