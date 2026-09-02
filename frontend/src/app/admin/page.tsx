import Link from "next/link";

export default function AdminPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">Admin</h1>
      <div className="grid grid-cols-3 gap-px bg-line hairline">
        <Link href="/admin/users" className="bg-paper p-6 hover:bg-line/10">
          <p className="font-display text-lg">Users</p>
          <p className="text-xs text-muted mt-1">View all accounts</p>
        </Link>
        <Link href="/admin/events" className="bg-paper p-6 hover:bg-line/10">
          <p className="font-display text-lg">Events</p>
          <p className="text-xs text-muted mt-1">Moderate events</p>
        </Link>
        <Link href="/admin/analytics" className="bg-paper p-6 hover:bg-line/10">
          <p className="font-display text-lg">Analytics</p>
          <p className="text-xs text-muted mt-1">Platform activity</p>
        </Link>
      </div>
    </div>
  );
}
