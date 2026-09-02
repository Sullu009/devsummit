"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "@/lib/api";
import type { EventAnalytics } from "@/lib/types";

export default function EventAnalyticsPage() {
  const { id } = useParams<{ id: string }>();
  const [stats, setStats] = useState<EventAnalytics | null>(null);

  useEffect(() => {
    api.get<EventAnalytics>(`/analytics/events/${id}`).then(setStats);
  }, [id]);

  if (!stats) return <div className="mx-auto max-w-4xl px-6 py-20 text-muted text-sm">Loading analytics…</div>;

  const funnel = [
    { stage: "Views", value: stats.views },
    { stage: "Bookings started", value: stats.bookings_created },
    { stage: "Confirmed", value: stats.bookings_confirmed },
  ];

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">Event analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-line hairline mb-10">
        <Metric label="Views" value={stats.views} />
        <Metric label="Conversion rate" value={`${stats.conversion_rate}%`} />
        <Metric label="Tickets sold" value={stats.tickets_sold} />
        <Metric label="Revenue" value={`₹${stats.revenue.toLocaleString("en-IN")}`} />
        <Metric label="Confirmed bookings" value={stats.bookings_confirmed} />
        <Metric label="Cancelled" value={stats.bookings_cancelled} />
        <Metric label="Attendance" value={stats.attendance_count} />
        <Metric label="Bookings started" value={stats.bookings_created} />
      </div>

      <h2 className="font-display text-xl mb-4">Booking funnel</h2>
      <div className="hairline p-6 h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={funnel}>
            <CartesianGrid strokeDasharray="3 3" stroke="#DCD7C9" vertical={false} />
            <XAxis dataKey="stage" tick={{ fontSize: 12, fill: "#6B6558" }} axisLine={{ stroke: "#DCD7C9" }} tickLine={false} />
            <YAxis tick={{ fontSize: 12, fill: "#6B6558" }} axisLine={false} tickLine={false} allowDecimals={false} />
            <Tooltip contentStyle={{ borderRadius: 0, border: "1px solid #DCD7C9", fontSize: 13 }} />
            <Bar dataKey="value" fill="#1F5E45" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-paper p-5">
      <p className="text-xs uppercase tracking-wide text-muted">{label}</p>
      <p className="font-display text-2xl mt-1">{value}</p>
    </div>
  );
}
