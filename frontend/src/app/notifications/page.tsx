"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { NotificationItem } from "@/lib/types";
import clsx from "clsx";

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[] | null>(null);

  const load = useCallback(() => {
    api.get<NotificationItem[]>("/notifications").then(setItems);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function markRead(id: string) {
    await api.patch(`/notifications/${id}/read`);
    load();
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="font-display text-3xl mb-8">Notifications</h1>

      {items && items.length === 0 && <p className="text-muted text-sm">Nothing here yet.</p>}

      <div className="space-y-px bg-line hairline">
        {items?.map((n) => (
          <button
            key={n.id}
            onClick={() => !n.is_read && markRead(n.id)}
            className={clsx("w-full text-left bg-paper p-5 hover:bg-line/20 transition-colors", !n.is_read && "relative")}
          >
            {!n.is_read && <span className="absolute left-2 top-6 w-1.5 h-1.5 rounded-full bg-forest" />}
            <div className="pl-3">
              <p className="text-sm font-medium">{n.title}</p>
              <p className="text-sm text-muted mt-0.5">{n.body}</p>
              <p className="text-xs text-muted mt-2 font-mono">{new Date(n.created_at).toLocaleString()}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
