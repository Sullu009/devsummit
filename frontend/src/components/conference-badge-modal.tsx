"use client";

import { useState } from "react";
import type { Booking, BookingItem } from "@/lib/types";

interface ConferenceBadgeModalProps {
  booking: Booking;
  item: BookingItem;
  eventTitle?: string;
  venueName?: string;
  city?: string;
  onClose: () => void;
}

export function ConferenceBadgeModal({
  booking,
  item,
  eventTitle = "DevSummit 2026: Global Developer Conference",
  venueName = "Metropolitan Tech Pavilion",
  city = "San Francisco, CA",
  onClose,
}: ConferenceBadgeModalProps) {
  const [attendeeName, setAttendeeName] = useState("Alex Developer");
  const [company, setCompany] = useState("CloudScale Technologies");
  const [roleTitle, setRoleTitle] = useState("Senior Systems Engineer");

  const ticketType = item.ticket_type_name || "General Attendee Pass";
  const isVip = ticketType.toLowerCase().includes("vip");
  const isWorkshop = ticketType.toLowerCase().includes("workshop");

  const badgeColor = isVip
    ? "from-amber-600 to-amber-500 text-amber-950"
    : isWorkshop
    ? "from-emerald-600 to-teal-600 text-white"
    : "from-indigo-600 to-violet-600 text-white";

  const passBadgeText = isVip
    ? "VIP ALL-ACCESS"
    : isWorkshop
    ? "WORKSHOP & LABS"
    : "ALL-ACCESS PASS";

  // Quick pseudo QR generator via Google Charts or QR Server for crisp vector SVG
  const qrData = encodeURIComponent(
    `https://devsummit.io/verify?ticket=${booking.id}&tier=${ticketType}&holder=${attendeeName}`
  );
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${qrData}&margin=4`;

  function handlePrint() {
    window.print();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4 overflow-y-auto print:p-0 print:bg-white">
      {/* Container */}
      <div className="relative w-full max-w-2xl bg-surface p-6 shadow-2xl hairline print:shadow-none print:border-none print:p-0">
        {/* Modal Controls - Hidden during print */}
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-line print:hidden">
          <div>
            <h2 className="font-display text-xl">Official Conference Badge</h2>
            <p className="text-xs text-muted">Customize attendee tag and print your official venue lanyard badge.</p>
          </div>
          <button
            onClick={onClose}
            className="text-muted hover:text-ink text-sm px-2 py-1 hairline hover:bg-paper transition-colors"
          >
            ✕ Close
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 items-start">
          {/* Customizer Sidebar - Hidden on print */}
          <div className="md:col-span-2 space-y-3 text-sm print:hidden">
            <h3 className="font-medium text-xs uppercase tracking-wider text-muted">Badge Personalization</h3>
            <div>
              <label className="block text-xs text-muted mb-1">Attendee Full Name</label>
              <input
                type="text"
                value={attendeeName}
                onChange={(e) => setAttendeeName(e.target.value)}
                className="w-full hairline px-3 py-1.5 text-sm bg-paper focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs text-muted mb-1">Company / Organization</label>
              <input
                type="text"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
                className="w-full hairline px-3 py-1.5 text-sm bg-paper focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-xs text-muted mb-1">Role / Designation</label>
              <input
                type="text"
                value={roleTitle}
                onChange={(e) => setRoleTitle(e.target.value)}
                className="w-full hairline px-3 py-1.5 text-sm bg-paper focus:outline-none"
              />
            </div>

            <div className="pt-3">
              <button
                onClick={handlePrint}
                className="w-full bg-ink text-paper py-2.5 px-4 font-medium text-sm flex items-center justify-center gap-2 hover:bg-ink/90 transition-colors shadow-sm"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
                </svg>
                Print / Save PDF Badge
              </button>
              <p className="text-[11px] text-muted text-center mt-1.5">
                Standard 4×6&quot; lanyard size with cut lines.
              </p>
            </div>
          </div>

          {/* BADGE PREVIEW (This is what prints) */}
          <div className="md:col-span-3 flex justify-center">
            <div
              id="printable-conference-badge"
              className="w-[320px] h-[480px] bg-white text-ink border-2 border-slate-300 rounded-2xl shadow-xl flex flex-col justify-between overflow-hidden relative print:border-2 print:border-black print:w-[320px] print:h-[480px] print:shadow-none"
            >
              {/* Lanyard Hole Punch Slot */}
              <div className="w-14 h-2.5 bg-slate-200 border border-slate-400 rounded-full mx-auto mt-3 print:border-black" />

              {/* Conference Header */}
              <div className="px-5 pt-3 pb-2 text-center">
                <div className="flex items-center justify-center gap-1.5 font-mono text-[11px] tracking-widest text-indigo-700 font-semibold uppercase">
                  <span>&gt;_</span> DEVSUMMIT GLOBAL
                </div>
                <h4 className="font-display font-bold text-sm tracking-tight leading-tight mt-0.5">
                  {eventTitle.split(":")[0]}
                </h4>
                <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                  {city} • Oct 24-25, 2026
                </p>
              </div>

              {/* Attendee Info Section */}
              <div className="px-5 text-center flex-1 flex flex-col justify-center">
                <div className="my-auto">
                  <h3 className="font-display font-extrabold text-2xl tracking-tight text-slate-900 leading-tight">
                    {attendeeName || "Attendee Name"}
                  </h3>
                  <p className="text-xs font-semibold text-slate-700 mt-1">
                    {roleTitle}
                  </p>
                  <p className="text-xs text-slate-500 font-medium">
                    {company}
                  </p>
                </div>
              </div>

              {/* Scannable Check-in QR Section */}
              <div className="bg-slate-50 border-t border-b border-slate-200 py-2.5 px-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={qrUrl}
                    alt="Check-in QR Code"
                    className="w-20 h-20 bg-white p-1 border border-slate-300 rounded"
                  />
                  <div className="text-left">
                    <p className="text-[9px] font-mono uppercase text-slate-400">Pass Serial</p>
                    <p className="text-[11px] font-mono font-bold text-slate-800">
                      #{booking.id.slice(0, 8).toUpperCase()}
                    </p>
                    <p className="text-[9px] text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                      VERIFIED PASS
                    </p>
                    <p className="text-[9px] text-slate-400 mt-0.5">
                      {venueName.slice(0, 22)}
                    </p>
                  </div>
                </div>
                <div className="text-right font-mono text-[9px] text-slate-400">
                  <span>ZONE</span>
                  <p className="font-bold text-slate-700">A / B / C</p>
                </div>
              </div>

              {/* Tier Banner Ribbon */}
              <div className={`py-2 px-4 bg-gradient-to-r ${badgeColor} text-center font-mono font-bold tracking-widest text-xs uppercase shadow-inner`}>
                {passBadgeText}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
