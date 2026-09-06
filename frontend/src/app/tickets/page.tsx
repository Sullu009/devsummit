"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Booking, BookingItem } from "@/lib/types";
import { ConferenceBadgeModal } from "@/components/conference-badge-modal";

export default function TicketsPage() {
  const [bookings, setBookings] = useState<Booking[] | null>(null);
  const [selectedBadge, setSelectedBadge] = useState<{ booking: Booking; item: BookingItem } | null>(null);

  useEffect(() => {
    api.get<Booking[]>("/bookings").then((all) => setBookings(all.filter((b) => b.status === "CONFIRMED")));
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <div className="mb-8">
        <h1 className="font-display text-4xl font-bold text-ink">My Conference Passes</h1>
        <p className="text-xs text-muted mt-1">
          Access your confirmed passes, verify serial numbers, and generate your printable venue lanyard badges.
        </p>
      </div>

      {bookings && bookings.length === 0 && (
        <div className="hairline p-8 text-center bg-surface">
          <p className="text-muted text-sm">No confirmed conference passes yet.</p>
        </div>
      )}

      <div className="space-y-6">
        {bookings?.map((b) => (
          <div key={b.id} className="hairline bg-surface flex flex-col sm:flex-row justify-between shadow-sm">
            {/* Left Serial / Ticket Notch */}
            <div className="px-6 py-6 sm:border-r border-dashed border-line flex flex-col justify-center items-center min-w-[130px] bg-paper/40">
              <span className="font-mono text-[10px] text-muted uppercase tracking-widest font-semibold">Pass Serial</span>
              <span className="font-mono font-bold text-lg text-indigo-700 mt-1">
                #{b.id.slice(0, 6).toUpperCase()}
              </span>
              <span className="text-[10px] text-emerald-600 font-semibold mt-1 uppercase font-mono">
                ● Confirmed
              </span>
            </div>

            {/* Center Info */}
            <div className="px-6 py-6 flex-1 flex flex-col justify-center">
              {b.items.map((i) => (
                <div key={i.id} className="mb-2">
                  <p className="text-base font-semibold text-ink">
                    {i.ticket_type_name}
                  </p>
                  <p className="text-xs text-muted">Quantity: {i.quantity} Pass</p>
                </div>
              ))}
              <div className="text-[11px] text-muted font-mono mt-2 space-y-0.5">
                <p>Booking ID: {b.id}</p>
                <p>Hold Ref: {b.reservation_id.slice(0, 8)}</p>
              </div>
            </div>

            {/* Right Action Button */}
            <div className="px-6 py-6 sm:border-l border-line flex items-center justify-center bg-paper/20">
              {b.items[0] && (
                <button
                  onClick={() => setSelectedBadge({ booking: b, item: b.items[0] })}
                  className="bg-ink text-paper px-4 py-2.5 text-xs font-semibold hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-sm rounded-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                  </svg>
                  Print Badge (PDF)
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Conference Badge Modal */}
      {selectedBadge && (
        <ConferenceBadgeModal
          booking={selectedBadge.booking}
          item={selectedBadge.item}
          onClose={() => setSelectedBadge(null)}
        />
      )}
    </div>
  );
}
