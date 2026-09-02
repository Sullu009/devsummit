"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Booking } from "@/lib/types";

function BookingSuccessContent() {
  const params = useSearchParams();
  const bookingId = params.get("booking_id");
  const [booking, setBooking] = useState<Booking | null>(null);

  useEffect(() => {
    if (!bookingId) return;
    api.get<Booking>(`/bookings/${bookingId}`).then(setBooking).catch(() => {});
  }, [bookingId]);

  return (
    <div className="mx-auto max-w-lg px-6 py-20 text-center">
      <p className="font-mono text-xs uppercase tracking-widest text-forest mb-3">Booking confirmed</p>
      <h1 className="font-display text-3xl mb-4">You&rsquo;re all set.</h1>
      <p className="text-muted text-sm mb-8">
        Your tickets are confirmed{booking ? ` — booking #${booking.id.slice(0, 8)}` : ""}. A confirmation notification has been sent.
      </p>
      <div className="flex gap-3 justify-center">
        <Link href="/tickets" className="bg-ink text-paper px-5 py-3 text-sm hover:bg-forest transition-colors">
          View my tickets
        </Link>
        <Link href="/events" className="hairline px-5 py-3 text-sm hover:bg-ink hover:text-paper transition-colors">
          Browse more events
        </Link>
      </div>
    </div>
  );
}

export default function BookingSuccessPage() {
  return (
    <Suspense fallback={<div className="mx-auto max-w-lg px-6 py-20 text-center text-muted text-sm">Loading…</div>}>
      <BookingSuccessContent />
    </Suspense>
  );
}
