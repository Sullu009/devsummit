"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Booking, EventDetail, FullSchedule, Speaker } from "@/lib/types";
import { StatusPill } from "@/components/status-pill";
import { ScheduleViewer } from "@/components/schedule-viewer";
import { SpeakersGrid } from "@/components/speakers-grid";

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const { user } = useAuth();

  const [event, setEvent] = useState<EventDetail | null>(null);
  const [schedule, setSchedule] = useState<FullSchedule | null>(null);
  const [speakers, setSpeakers] = useState<Speaker[]>([]);
  const [activeTab, setActiveTab] = useState<"overview" | "schedule" | "speakers">("overview");

  const [error, setError] = useState<string | null>(null);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [reserving, setReserving] = useState(false);
  const [reserveError, setReserveError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<EventDetail>(`/events/${id}`)
      .then((ev) => {
        setEvent(ev);
        if (ev.speakers && ev.speakers.length > 0) {
          setSpeakers(ev.speakers);
        }
      })
      .catch((e) => setError(e.message));

    // Fetch schedule and speakers
    api
      .get<FullSchedule>(`/events/${id}/schedule`)
      .then(setSchedule)
      .catch(() => {});

    api
      .get<Speaker[]>(`/events/${id}/speakers`)
      .then((spks) => {
        if (spks && spks.length > 0) setSpeakers(spks);
      })
      .catch(() => {});
  }, [id]);

  if (error) {
    return <div className="mx-auto max-w-4xl px-6 py-20 text-rust">Could not load this event: {error}</div>;
  }
  if (!event) {
    return <div className="mx-auto max-w-4xl px-6 py-20 text-muted text-sm">Loading conference details…</div>;
  }

  const total = event.ticket_types.reduce((sum, tt) => sum + (quantities[tt.id] || 0) * Number(tt.price), 0);
  const anySelected = Object.values(quantities).some((q) => q > 0);

  async function handleReserve() {
    if (!user) {
      router.push(`/login?next=/events/${id}`);
      return;
    }
    setReserveError(null);
    setReserving(true);
    try {
      const items = Object.entries(quantities)
        .filter(([, qty]) => qty > 0)
        .map(([ticket_type_id, quantity]) => ({ ticket_type_id, quantity }));

      const booking = await api.post<Booking>(
        "/bookings/reserve",
        { event_id: event!.id, items },
        { idempotencyKey: `reserve-${event!.id}-${Date.now()}` }
      );
      router.push(`/checkout?booking_id=${booking.id}`);
    } catch (err) {
      setReserveError(err instanceof ApiError ? err.message : "Could not reserve tickets. Please try again.");
    } finally {
      setReserving(false);
    }
  }

  const hasConferenceData = (event.tracks && event.tracks.length > 0) || (speakers && speakers.length > 0) || schedule;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      {/* Category / Status Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs uppercase tracking-widest text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded font-semibold">
            {event.category} CONFERENCE
          </span>
          {event.city && (
            <span className="text-xs text-muted font-mono">📍 {event.city}</span>
          )}
        </div>
        <StatusPill status={event.status} />
      </div>

      <h1 className="font-display text-4xl md:text-5xl font-bold mb-6 text-ink">{event.title}</h1>

      {/* Conference Navigation Tabs */}
      {hasConferenceData && (
        <div className="flex border-b border-line mb-8 gap-8 text-sm">
          <button
            onClick={() => setActiveTab("overview")}
            className={`pb-3.5 font-medium transition-colors relative flex items-center gap-2 ${
              activeTab === "overview"
                ? "text-ink font-semibold"
                : "text-muted hover:text-ink"
            }`}
          >
            <span>Overview & Passes</span>
            {activeTab === "overview" && <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-ink" />}
          </button>

          <button
            onClick={() => setActiveTab("schedule")}
            className={`pb-3.5 font-medium transition-colors relative flex items-center gap-2 ${
              activeTab === "schedule"
                ? "text-ink font-semibold"
                : "text-muted hover:text-ink"
            }`}
          >
            <span>Multi-Track Schedule</span>
            {schedule?.days && (
              <span className="text-[10px] bg-indigo-100 text-indigo-800 font-mono px-1.5 py-0.2 rounded-full font-bold">
                {schedule.days.length} Days
              </span>
            )}
            {activeTab === "schedule" && <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-ink" />}
          </button>

          <button
            onClick={() => setActiveTab("speakers")}
            className={`pb-3.5 font-medium transition-colors relative flex items-center gap-2 ${
              activeTab === "speakers"
                ? "text-ink font-semibold"
                : "text-muted hover:text-ink"
            }`}
          >
            <span>Featured Speakers</span>
            {speakers.length > 0 && (
              <span className="text-[10px] bg-indigo-100 text-indigo-800 font-mono px-1.5 py-0.2 rounded-full font-bold">
                {speakers.length}
              </span>
            )}
            {activeTab === "speakers" && <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-ink" />}
          </button>
        </div>
      )}

      {/* TAB 1: OVERVIEW & TICKETS */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Metadata Box */}
            <div className="hairline p-5 grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm bg-surface">
              <div>
                <p className="text-xs font-mono uppercase tracking-wide text-muted mb-1">Conference Dates</p>
                <p className="font-semibold text-ink">
                  {new Date(event.starts_at).toLocaleString("en-US", { dateStyle: "full", timeStyle: "short" })}
                </p>
                <p className="text-muted text-xs mt-0.5">
                  Through {new Date(event.ends_at).toLocaleString("en-US", { dateStyle: "medium", timeStyle: "short" })}
                </p>
              </div>
              <div>
                <p className="text-xs font-mono uppercase tracking-wide text-muted mb-1">Venue & Location</p>
                <p className="font-semibold text-ink">{event.venue_name || "TBA"}</p>
                <p className="text-muted text-xs mt-0.5">
                  {event.venue_address}{event.venue_address && event.city ? ", " : ""}{event.city}
                </p>
              </div>
            </div>

            {/* About */}
            <div>
              <h2 className="font-display text-2xl font-bold mb-3">About this conference</h2>
              <p className="text-sm leading-relaxed whitespace-pre-wrap text-ink/90">{event.description || "No description provided."}</p>
            </div>

            {/* Featured Tracks Preview */}
            {event.tracks && event.tracks.length > 0 && (
              <div>
                <h3 className="font-display text-xl font-bold mb-3">Conference Tracks</h3>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {event.tracks.map((tr) => (
                    <div key={tr.id} className="hairline p-4 bg-surface border-t-2" style={{ borderTopColor: tr.color_code || "#6366F1" }}>
                      <p className="font-semibold text-sm text-ink">{tr.name}</p>
                      <p className="text-xs text-muted mt-1 leading-normal">{tr.description}</p>
                      <p className="text-[11px] font-mono text-muted mt-2">📍 {tr.room_location}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Ticket Selection Sidebar */}
          <div className="hairline p-6 h-fit sticky top-24 bg-surface shadow-sm">
            <h2 className="font-display text-xl font-bold mb-1">Select Conference Pass</h2>
            <p className="text-xs text-muted mb-4">Official lanyard pass with QR check-in & badge included.</p>

            {event.ticket_types.length === 0 && <p className="text-sm text-muted">No passes currently available.</p>}

            <div className="space-y-4">
              {event.ticket_types.map((tt) => (
                <div key={tt.id} className="border-b border-line pb-3 last:border-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-ink">{tt.name}</p>
                      {tt.description && (
                        <p className="text-[11px] text-muted leading-tight mt-0.5">{tt.description}</p>
                      )}
                      <p className="font-mono text-sm text-indigo-700 font-bold mt-1">₹{Number(tt.price).toLocaleString("en-IN")}</p>
                    </div>
                    <div className="flex items-center gap-2 pt-1">
                      <button
                        type="button"
                        onClick={() => setQuantities((q) => ({ ...q, [tt.id]: Math.max(0, (q[tt.id] || 0) - 1) }))}
                        className="hairline w-7 h-7 text-sm hover:bg-ink hover:text-paper transition-colors font-bold"
                      >
                        −
                      </button>
                      <span className="font-mono text-sm w-5 text-center">{quantities[tt.id] || 0}</span>
                      <button
                        type="button"
                        disabled={(quantities[tt.id] || 0) >= tt.quantity_available}
                        onClick={() => setQuantities((q) => ({ ...q, [tt.id]: Math.min(tt.quantity_available, (q[tt.id] || 0) + 1) }))}
                        className="hairline w-7 h-7 text-sm hover:bg-ink hover:text-paper transition-colors disabled:opacity-30 font-bold"
                      >
                        +
                      </button>
                    </div>
                  </div>
                  <p className="text-[10px] font-mono text-muted mt-1.5">
                    {tt.quantity_available > 0 ? `${tt.quantity_available} passes remaining` : "Sold out"}
                  </p>
                </div>
              ))}
            </div>

            {anySelected && (
              <div className="flex items-center justify-between mt-5 pt-4 border-t border-line text-sm">
                <span className="text-muted font-medium">Subtotal</span>
                <span className="font-mono font-bold text-lg text-ink">₹{total.toLocaleString("en-IN")}</span>
              </div>
            )}

            {reserveError && <p className="text-rust text-xs mt-3">{reserveError}</p>}

            <button
              onClick={handleReserve}
              disabled={!anySelected || reserving || event.status !== "PUBLISHED"}
              className="w-full bg-ink text-paper px-4 py-3.5 text-sm font-semibold mt-4 hover:bg-indigo-700 transition-colors disabled:opacity-40 shadow-sm"
            >
              {reserving ? "Holding Passes in Redis…" : "Reserve Passes & Proceed"}
            </button>
            <p className="text-[11px] text-muted mt-2 text-center">
              🔒 Real-time hold with 10-min reservation TTL.
            </p>
          </div>
        </div>
      )}

      {/* TAB 2: MULTI-TRACK SCHEDULE */}
      {activeTab === "schedule" && (
        <div className="bg-surface hairline p-6">
          <div className="mb-6">
            <h2 className="font-display text-2xl font-bold">Conference Agenda & Multi-Track Schedule</h2>
            <p className="text-xs text-muted mt-1">
              Explore keynotes, concurrent multi-track deep dives, and hands-on coding labs.
            </p>
          </div>
          <ScheduleViewer schedule={schedule} tracks={event.tracks} fallbackSessions={event.sessions} />
        </div>
      )}

      {/* TAB 3: FEATURED SPEAKERS */}
      {activeTab === "speakers" && (
        <div>
          <div className="mb-6">
            <h2 className="font-display text-2xl font-bold">Keynote & Track Speakers</h2>
            <p className="text-xs text-muted mt-1">
              Learn directly from foundational researchers, distributed systems architects, and open-source creators.
            </p>
          </div>
          <SpeakersGrid speakers={speakers.length > 0 ? speakers : (event.speakers || [])} />
        </div>
      )}
    </div>
  );
}
