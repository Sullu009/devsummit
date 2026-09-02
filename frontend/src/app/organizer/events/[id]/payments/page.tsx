"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import type { EventRevenue } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";

export default function EventPaymentsPage() {
  const { id } = useParams<{ id: string }>();
  const [revenue, setRevenue] = useState<EventRevenue | null>(null);

  useEffect(() => {
    api.get<EventRevenue>(`/payments/events/${id}/revenue`).then(setRevenue);
  }, [id]);

  if (!revenue) return <div className="mx-auto max-w-4xl px-6 py-20 text-muted text-sm">Loading revenue…</div>;

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">Payments &amp; revenue</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-px bg-line hairline mb-10">
        <Metric label="Gross revenue" value={`₹${revenue.gross_revenue.toLocaleString("en-IN")}`} accent />
        <Metric label="Net revenue" value={`₹${revenue.net_revenue.toLocaleString("en-IN")}`} />
        <Metric label="Paid bookings" value={revenue.paid_bookings} />
        <Metric label="Refunded" value={revenue.refunded_count} />
        <Metric label="Payment failures" value={revenue.payment_failures} />
        <Metric label="Success rate" value={`${revenue.payment_success_rate}%`} />
      </div>

      <h2 className="font-display text-xl mb-4">Recent transactions</h2>
      <table className="w-full text-sm hairline border-collapse">
        <thead>
          <tr className="text-left text-xs uppercase tracking-wide text-muted border-b border-line">
            <th className="p-3">Payment</th>
            <th className="p-3">Booking</th>
            <th className="p-3">Amount</th>
            <th className="p-3">Status</th>
            <th className="p-3">Date</th>
          </tr>
        </thead>
        <tbody>
          {revenue.recent_transactions.map((tx) => (
            <tr key={tx.id} className="border-b border-line last:border-0">
              <td className="p-3 font-mono text-xs">{tx.razorpay_payment_id?.slice(0, 14) || tx.razorpay_order_id.slice(0, 14)}</td>
              <td className="p-3 font-mono text-xs">#{tx.booking_id.slice(0, 8)}</td>
              <td className="p-3 font-mono">₹{Number(tx.amount).toLocaleString("en-IN")}</td>
              <td className="p-3">
                <StatusPill status={tx.status} />
              </td>
              <td className="p-3 text-muted">{new Date(tx.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {revenue.recent_transactions.length === 0 && <p className="text-muted text-sm mt-6">No transactions yet.</p>}
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string | number; accent?: boolean }) {
  return (
    <div className="bg-paper p-5">
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className={`font-display text-2xl mt-1 ${accent ? "text-forest" : ""}`}>{value}</p>
    </div>
  );
}
