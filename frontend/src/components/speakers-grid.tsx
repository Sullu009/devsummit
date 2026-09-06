"use client";

import { useState } from "react";
import type { Speaker, Session } from "@/lib/types";

interface SpeakersGridProps {
  speakers: Speaker[];
}

export function SpeakersGrid({ speakers }: SpeakersGridProps) {
  const [selectedSpeaker, setSelectedSpeaker] = useState<Speaker | null>(null);

  if (!speakers || speakers.length === 0) {
    return (
      <div className="py-12 text-center text-muted hairline bg-paper/40 p-6">
        <p className="text-sm">Speakers for this event will be announced shortly.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {speakers.map((spk) => (
          <div
            key={spk.id}
            onClick={() => setSelectedSpeaker(spk)}
            className="hairline bg-surface p-5 flex flex-col justify-between hover:border-ink/60 transition-all cursor-pointer group hover:shadow-sm"
          >
            <div>
              {/* Speaker Avatar & Company Pill */}
              <div className="flex items-start justify-between gap-3 mb-4">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={spk.avatar_url || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80"}
                  alt={spk.name}
                  className="w-16 h-16 rounded-full object-cover border border-line group-hover:scale-105 transition-transform"
                />
                <span className="text-[11px] font-mono font-medium px-2 py-0.5 bg-paper hairline rounded text-muted">
                  {spk.company}
                </span>
              </div>

              {/* Speaker Name & Role */}
              <h3 className="font-display font-semibold text-lg text-ink group-hover:text-indigo-600 transition-colors">
                {spk.name}
              </h3>
              <p className="text-xs text-muted font-medium mt-0.5">
                {spk.role_title}
              </p>

              {/* Bio Preview */}
              <p className="text-xs text-ink/80 mt-2.5 line-clamp-3 leading-relaxed">
                {spk.bio}
              </p>
            </div>

            {/* Bottom: Social Links & Talks Count */}
            <div className="pt-4 mt-4 border-t border-line/60 flex items-center justify-between text-xs">
              <div className="flex items-center gap-3 text-muted" onClick={(e) => e.stopPropagation()}>
                {spk.github_url && (
                  <a
                    href={spk.github_url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-ink font-mono text-[11px]"
                    title="GitHub"
                  >
                    GitHub ↗
                  </a>
                )}
                {spk.linkedin_url && (
                  <a
                    href={spk.linkedin_url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-ink font-mono text-[11px]"
                    title="LinkedIn"
                  >
                    LinkedIn ↗
                  </a>
                )}
                {spk.twitter_url && (
                  <a
                    href={spk.twitter_url}
                    target="_blank"
                    rel="noreferrer"
                    className="hover:text-ink font-mono text-[11px]"
                    title="Twitter / X"
                  >
                    X ↗
                  </a>
                )}
              </div>
              <span className="text-[11px] text-indigo-600 font-medium group-hover:underline">
                View Talks →
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Speaker Details Modal */}
      {selectedSpeaker && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="max-w-xl w-full bg-surface hairline p-6 shadow-2xl relative max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setSelectedSpeaker(null)}
              className="absolute top-4 right-4 text-muted hover:text-ink text-sm px-2 py-1 hairline"
            >
              ✕
            </button>

            <div className="flex items-start gap-4 mb-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={selectedSpeaker.avatar_url}
                alt={selectedSpeaker.name}
                className="w-20 h-20 rounded-full object-cover border border-line"
              />
              <div>
                <h2 className="font-display text-2xl font-bold text-ink">{selectedSpeaker.name}</h2>
                <p className="text-sm font-medium text-slate-700">{selectedSpeaker.role_title}</p>
                <p className="text-xs text-muted font-mono mt-0.5">{selectedSpeaker.company}</p>

                {/* Social links */}
                <div className="flex items-center gap-3 mt-2 text-xs">
                  {selectedSpeaker.github_url && (
                    <a href={selectedSpeaker.github_url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">
                      GitHub
                    </a>
                  )}
                  {selectedSpeaker.linkedin_url && (
                    <a href={selectedSpeaker.linkedin_url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">
                      LinkedIn
                    </a>
                  )}
                  {selectedSpeaker.twitter_url && (
                    <a href={selectedSpeaker.twitter_url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">
                      Twitter/X
                    </a>
                  )}
                </div>
              </div>
            </div>

            <div className="my-4">
              <h4 className="text-xs font-mono uppercase tracking-wider text-muted mb-1">Speaker Biography</h4>
              <p className="text-sm text-ink/90 leading-relaxed whitespace-pre-wrap">{selectedSpeaker.bio}</p>
            </div>

            {selectedSpeaker.sessions && selectedSpeaker.sessions.length > 0 && (
              <div className="mt-6 pt-4 border-t border-line">
                <h4 className="text-xs font-mono uppercase tracking-wider text-muted mb-3">Sessions by this Speaker</h4>
                <div className="space-y-2">
                  {selectedSpeaker.sessions.map((sess: Session) => (
                    <div key={sess.id} className="p-3 hairline bg-paper/40">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono px-1.5 py-0.5 bg-indigo-100 text-indigo-900 rounded font-semibold">
                          {sess.session_type}
                        </span>
                        {sess.track && (
                          <span className="text-xs text-muted">{sess.track.name}</span>
                        )}
                      </div>
                      <p className="font-medium text-sm text-ink">{sess.title}</p>
                      <p className="text-xs text-muted mt-1 line-clamp-2">{sess.abstract}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
