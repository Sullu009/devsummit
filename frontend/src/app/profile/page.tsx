"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { User } from "@/lib/types";

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [fullName, setFullName] = useState("");
  const [phone, setPhone] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name);
      setPhone(user.phone || "");
    }
  }, [user]);

  if (!user) return <div className="mx-auto max-w-md px-6 py-20 text-muted text-sm">Please log in to view your profile.</div>;

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    try {
      await api.patch<User>("/auth/me", { full_name: fullName, phone: phone || null });
      await refreshUser();
      setSaved(true);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-6 py-12">
      <h1 className="font-display text-3xl mb-1">Profile</h1>
      <p className="text-muted text-sm mb-8">
        {user.email} · <span className="uppercase text-xs tracking-wide">{user.role}</span>
      </p>

      <form onSubmit={save} className="space-y-4">
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Full name</label>
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Phone</label>
          <input value={phone} onChange={(e) => setPhone(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>
        <button type="submit" disabled={saving} className="bg-ink text-paper px-5 py-2.5 text-sm hover:bg-forest transition-colors disabled:opacity-50">
          {saving ? "Saving…" : "Save changes"}
        </button>
        {saved && <p className="text-forest text-xs">Saved.</p>}
      </form>
    </div>
  );
}
