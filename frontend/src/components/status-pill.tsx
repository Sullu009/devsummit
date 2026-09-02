import clsx from "clsx";

const STATUS_STYLES: Record<string, string> = {
  DRAFT: "text-muted",
  PUBLISHED: "text-forest",
  CANCELLED: "text-rust",
  PENDING_PAYMENT: "text-gold",
  CONFIRMED: "text-forest",
  EXPIRED: "text-muted",
  REFUND_PENDING: "text-gold",
  REFUNDED: "text-muted",
  SUCCEEDED: "text-forest",
  FAILED: "text-rust",
  CREATED: "text-gold",
};

const DOT_STYLES: Record<string, string> = {
  DRAFT: "bg-muted",
  PUBLISHED: "bg-forest",
  CANCELLED: "bg-rust",
  PENDING_PAYMENT: "bg-gold",
  CONFIRMED: "bg-forest",
  EXPIRED: "bg-muted",
  REFUND_PENDING: "bg-gold",
  REFUNDED: "bg-muted",
  SUCCEEDED: "bg-forest",
  FAILED: "bg-rust",
  CREATED: "bg-gold",
};

export function StatusPill({ status }: { status: string }) {
  const label = status.replace(/_/g, " ");
  return (
    <span className={clsx("inline-flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide", STATUS_STYLES[status] ?? "text-muted")}>
      <span className={clsx("status-dot", DOT_STYLES[status] ?? "bg-muted")} />
      {label}
    </span>
  );
}
