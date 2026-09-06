"use client";

import { useState } from "react";
import type { FullSchedule, Session, Track } from "@/lib/types";

interface ScheduleViewerProps {
  schedule: FullSchedule | null;
  tracks?: Track[];
  fallbackSessions?: Session[];
}

export function ScheduleViewer({ schedule, tracks = [], fallbackSessions = [] }: ScheduleViewerProps) {
  const [activeDayIndex, setActiveDayIndex] = useState(0);
  const [selectedTrackId, setSelectedTrackId] = useState<string | "ALL">("ALL");
  const [activeSessionModal, setActiveSessionModal] = useState<Session | null>(null);

  // If schedule API is available with days
  const days = schedule?.days || [];
  const currentDay = days[activeDayIndex];

  // Available tracks to filter
  const allTracks = currentDay?.tracks || tracks;

  // Filter slots and sessions based on selectedTrackId
  const slots = currentDay?.slots || [];
  const filteredSlots = slots.map((slot) => ({
    ...slot,
    sessions: slot.sessions.filter((s) => {
      if (selectedTrackId === "ALL") return true;
      return s.track_id === selectedTrackId;
    }),
  })).filter((slot) => slot.sessions.length > 0);

  if (!schedule && fallbackSessions.length === 0) {
    return (
      <div className="py-12 text-center text-muted hairline bg-paper/40 p-6">
        <p className="text-sm">Schedule is currently being finalized by conference chairs.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Day Selector Navigation Tabs */}
      {days.length > 1 && (
        <div className="flex border-b border-line gap-4">
          {days.map((day, idx) => (
            <button
              key={day.date}
              onClick={() => {
                setActiveDayIndex(idx);
                setSelectedTrackId("ALL");
              }}
              className={`pb-3 font-medium text-sm transition-colors relative ${
                activeDayIndex === idx
                  ? "text-ink font-semibold"
                  : "text-muted hover:text-ink"
              }`}
            >
              {day.date_label}
              {activeDayIndex === idx && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-ink" />
              )}
            </button>
          ))}
        </div>
      )}

      {/* Track Filter Filter Chips */}
      {allTracks.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs uppercase tracking-wider text-muted mr-1 font-mono">Filter Track:</span>
          <button
            onClick={() => setSelectedTrackId("ALL")}
            className={`text-xs px-3 py-1 rounded-full transition-colors ${
              selectedTrackId === "ALL"
                ? "bg-ink text-paper font-medium"
                : "hairline hover:bg-paper text-muted"
            }`}
          >
            All Tracks
          </button>
          {allTracks.map((tr) => (
            <button
              key={tr.id}
              onClick={() => setSelectedTrackId(tr.id)}
              className={`text-xs px-3 py-1 rounded-full flex items-center gap-1.5 transition-colors ${
                selectedTrackId === tr.id
                  ? "bg-ink text-paper font-medium"
                  : "hairline hover:bg-paper text-muted"
              }`}
            >
              <span
                className="w-2 h-2 rounded-full inline-block"
                style={{ backgroundColor: tr.color_code || "#6366F1" }}
              />
              {tr.name.split(":")[0]}
            </button>
          ))}
        </div>
      )}

      {/* Timetable Schedule Grid */}
      <div className="space-y-6 mt-4">
        {filteredSlots.length === 0 ? (
          <div className="p-8 text-center text-muted hairline text-sm">
            No sessions match the selected track filter for this day.
          </div>
        ) : (
          filteredSlots.map((slot) => (
            <div key={slot.time_label} className="grid grid-cols-1 md:grid-cols-12 gap-4 items-start">
              {/* Time Column */}
              <div className="md:col-span-3 pt-1">
                <span className="font-mono text-xs font-semibold text-ink px-2.5 py-1 bg-paper hairline inline-block rounded">
                  {slot.time_label}
                </span>
              </div>

              {/* Sessions in this slot */}
              <div className="md:col-span-9 space-y-3">
                {slot.sessions.map((sess) => {
                  const isKeynote = sess.session_type === "KEYNOTE";
                  const isWorkshop = sess.session_type === "WORKSHOP";

                  return (
                    <div
                      key={sess.id}
                      onClick={() => setActiveSessionModal(sess)}
                      className={`p-4 hairline transition-all cursor-pointer hover:border-ink/60 hover:shadow-sm bg-surface ${
                        isKeynote ? "border-l-4 border-l-indigo-600" : isWorkshop ? "border-l-4 border-l-emerald-600" : ""
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase font-semibold ${
                              isKeynote
                                ? "bg-indigo-100 text-indigo-800"
                                : isWorkshop
                                ? "bg-emerald-100 text-emerald-800"
                                : "bg-slate-100 text-slate-800"
                            }`}
                          >
                            {sess.session_type}
                          </span>
                          {sess.track && (
                            <span className="text-xs text-muted font-medium flex items-center gap-1">
                              <span
                                className="w-1.5 h-1.5 rounded-full"
                                style={{ backgroundColor: sess.track.color_code }}
                              />
                              {sess.track.name}
                            </span>
                          )}
                        </div>
                        {sess.track?.room_location && (
                          <span className="text-[11px] text-muted font-mono bg-paper px-2 py-0.5 rounded">
                            📍 {sess.track.room_location}
                          </span>
                        )}
                      </div>

                      <h3 className="font-display text-base font-semibold text-ink group-hover:text-indigo-600 transition-colors">
                        {sess.title}
                      </h3>

                      <p className="text-xs text-muted line-clamp-2 mt-1 leading-relaxed">
                        {sess.abstract}
                      </p>

                      {/* Speaker row */}
                      {sess.speaker && (
                        <div className="flex items-center gap-2.5 mt-3 pt-3 border-t border-line/60">
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={sess.speaker.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80"}
                            alt={sess.speaker.name}
                            className="w-6 h-6 rounded-full object-cover border border-line"
                          />
                          <span className="text-xs font-medium text-ink">
                            {sess.speaker.name}
                          </span>
                          <span className="text-xs text-muted">
                            • {sess.speaker.role_title}, {sess.speaker.company}
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Abstract Modal */}
      {activeSessionModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="max-w-xl w-full bg-surface hairline p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setActiveSessionModal(null)}
              className="absolute top-4 right-4 text-muted hover:text-ink text-sm px-2 py-1 hairline"
            >
              ✕
            </button>

            <div className="flex items-center gap-2 mb-3">
              <span className="text-[11px] font-mono px-2 py-0.5 bg-indigo-100 text-indigo-900 rounded font-semibold uppercase">
                {activeSessionModal.session_type}
              </span>
              {activeSessionModal.track && (
                <span className="text-xs text-muted flex items-center gap-1 font-medium">
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: activeSessionModal.track.color_code }}
                  />
                  {activeSessionModal.track.name}
                </span>
              )}
            </div>

            <h2 className="font-display text-2xl font-bold mb-3">{activeSessionModal.title}</h2>

            {activeSessionModal.track?.room_location && (
              <p className="text-xs font-mono text-muted mb-4">
                Room: {activeSessionModal.track.room_location}
              </p>
            )}

            <div className="my-4">
              <h4 className="text-xs font-mono uppercase tracking-wider text-muted mb-1">Session Abstract</h4>
              <p className="text-sm text-ink/90 leading-relaxed whitespace-pre-wrap">
                {activeSessionModal.abstract}
              </p>
            </div>

            {activeSessionModal.speaker && (
              <div className="mt-6 pt-4 border-t border-line">
                <h4 className="text-xs font-mono uppercase tracking-wider text-muted mb-2">Featured Speaker</h4>
                <div className="flex items-start gap-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={activeSessionModal.speaker.avatar_url}
                    alt={activeSessionModal.speaker.name}
                    className="w-12 h-12 rounded-full object-cover border border-line"
                  />
                  <div>
                    <h5 className="font-medium text-sm text-ink">{activeSessionModal.speaker.name}</h5>
                    <p className="text-xs text-muted">
                      {activeSessionModal.speaker.role_title} at {activeSessionModal.speaker.company}
                    </p>
                    <p className="text-xs text-muted mt-1 leading-normal">
                      {activeSessionModal.speaker.bio}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
