"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Booking } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function EventBookingsPage() {
  const { id } = useParams<{ id: string }>();
  const [bookings, setBookings] = useState<Booking[] | null>(null);

  useEffect(() => {
    api.get<Booking[]>(`/bookings/event/${id}`).then(setBookings);
  }, [id]);

  const confirmed = bookings?.filter((b) => b.status === "CONFIRMED").length ?? 0;
  const totalTickets = bookings
    ?.filter((b) => b.status === "CONFIRMED")
    .reduce((sum, b) => sum + b.items.reduce((s, i) => s + i.quantity, 0), 0) ?? 0;

  return (
    <div className="mx-auto max-w-5xl px-6 py-12">
      <h1 className="font-display text-3xl mb-1">Attendees &amp; bookings</h1>
      <p className="text-muted text-sm mb-8">{confirmed} confirmed bookings · {totalTickets} tickets sold</p>

      <table className="w-full text-sm hairline border-collapse">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wide text-muted border-b border-line">
            <th className="p-3">Booking</th>
            <th className="p-3">Tickets</th>
            <th className="p-3">Amount</th>
            <th className="p-3">Status</th>
            <th className="p-3">Date</th>
          </tr>
        </thead>
        <tbody>
          {bookings?.map((b) => (
            <tr key={b.id} className="border-b border-line last:border-0">
              <td className="p-3 font-mono text-xs">#{b.id.slice(0, 8)}</td>
              <td className="p-3">{b.items.map((i) => `${i.quantity}× ${i.ticket_type_name}`).join(", ")}</td>
              <td className="p-3 font-mono">₹{Number(b.total_amount).toLocaleString("en-IN")}</td>
              <td className="p-3">
                <StatusPill status={b.status} />
              </td>
              <td className="p-3 text-muted">{new Date(b.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {bookings && bookings.length === 0 && <p className="text-muted text-sm mt-6">No bookings yet for this event.</p>}
    </div>
  );
}
