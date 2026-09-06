"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export function Navbar() {
  const { user, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  const isOrganizerArea = pathname?.startsWith("/organizer");
  const isAdminArea = pathname?.startsWith("/admin");

  return (
    <header className="hairline border-x-0 border-t-0 sticky top-0 z-40 bg-paper/95 backdrop-blur-none">
      <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-display text-xl tracking-tight flex items-center gap-1 font-bold">
          <span className="font-mono text-indigo-600 font-extrabold text-base">&gt;_</span>
          <span>Dev</span>
          <span className="text-indigo-600">Summit</span>
        </Link>

        <nav className="hidden md:flex items-center gap-7 text-sm font-medium">
          <Link href="/events" className={pathname === "/events" ? "text-ink font-semibold" : "text-muted hover:text-ink"}>
            Conferences & Labs
          </Link>
          {user && (
            <>
              <Link href="/tickets" className={pathname === "/tickets" ? "text-ink font-semibold" : "text-muted hover:text-ink"}>
                My Passes & Badges
              </Link>
              <Link href="/my-bookings" className={pathname === "/my-bookings" ? "text-ink font-semibold" : "text-muted hover:text-ink"}>
                Orders
              </Link>
            </>
          )}
          {user && (user.role === "ORGANIZER" || user.role === "ADMIN") && (
            <Link href="/organizer" className={isOrganizerArea ? "text-ink font-semibold" : "text-muted hover:text-ink"}>
              Organizer Portal
            </Link>
          )}
          {user && user.role === "ADMIN" && (
            <Link href="/admin" className={isAdminArea ? "text-ink font-semibold" : "text-muted hover:text-ink"}>
              Admin
            </Link>
          )}
        </nav>

        <div className="flex items-center gap-4 text-sm">
          {user ? (
            <>
              <Link href="/notifications" className="text-muted hover:text-ink">
                Notifications
              </Link>
              <Link href="/profile" className="text-muted hover:text-ink font-medium">
                {user.full_name.split(" ")[0]}
              </Link>
              <button
                onClick={() => {
                  logout();
                  router.push("/");
                }}
                className="hairline px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-muted hover:text-ink">
                Log in
              </Link>
              <Link href="/register" className="hairline px-3 py-1.5 hover:bg-ink hover:text-paper transition-colors">
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
