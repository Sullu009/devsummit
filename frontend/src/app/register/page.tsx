"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import clsx from "clsx";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import type { UserRole } from "@/lib/types";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("ATTENDEE");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register(email, fullName, password, role);
      router.push(role === "ORGANIZER" ? "/organizer" : "/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm px-6 py-20">
      <h1 className="font-display text-3xl mb-1">Create your account</h1>
      <p className="text-muted text-sm mb-8">Book tickets or start hosting events on EventSphere.</p>

      <div className="flex hairline mb-6 text-sm">
        <button
          type="button"
          onClick={() => setRole("ATTENDEE")}
          className={clsx("flex-1 py-2.5", role === "ATTENDEE" ? "bg-ink text-paper" : "text-muted")}
        >
          Attendee
        </button>
        <button
          type="button"
          onClick={() => setRole("ORGANIZER")}
          className={clsx("flex-1 py-2.5 border-l border-line", role === "ORGANIZER" ? "bg-ink text-paper" : "text-muted")}
        >
          Organizer
        </button>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Full name</label>
          <input required value={fullName} onChange={(e) => setFullName(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
        </div>
        <div>
          <label className="text-xs uppercase tracking-wide text-muted block mb-1.5">Password</label>
          <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} className="w-full hairline px-3 py-2.5 bg-surface focus:outline-none focus:border-ink" />
          <p className="text-xs text-muted mt-1">At least 8 characters.</p>
        </div>

        {error && <p className="text-rust text-sm">{error}</p>}

        <button type="submit" disabled={submitting} className="w-full bg-ink text-paper px-5 py-3 text-sm hover:bg-forest transition-colors disabled:opacity-50">
          {submitting ? "Creating account…" : "Create account"}
        </button>
      </form>

      <p className="text-sm text-muted mt-6">
        Already have an account?{" "}
        <Link href="/login" className="text-forest hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
