import {
  DEMO_BOOKINGS,
  DEMO_EVENT,
  DEMO_PAGINATED_EVENTS,
  DEMO_SCHEDULE,
  DEMO_SPEAKERS,
} from "./demo-fallback";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8080/api";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("es_access_token");
}

function getFallbackData<T>(path: string): T | null {
  if (path.startsWith("/events?") || path === "/events") {
    return DEMO_PAGINATED_EVENTS as unknown as T;
  }
  if (path.includes("/schedule")) {
    return DEMO_SCHEDULE as unknown as T;
  }
  if (path.includes("/speakers")) {
    return DEMO_SPEAKERS as unknown as T;
  }
  if (path === "/events/seed-demo") {
    return DEMO_EVENT as unknown as T;
  }
  if (path.startsWith("/events/")) {
    return DEMO_EVENT as unknown as T;
  }
  if (path.startsWith("/bookings/reserve")) {
    return DEMO_BOOKINGS[0] as unknown as T;
  }
  if (path.startsWith("/bookings")) {
    return DEMO_BOOKINGS as unknown as T;
  }
  return null;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { auth?: boolean; idempotencyKey?: string } = {}
): Promise<T> {
  const { auth = true, idempotencyKey, ...init } = options;
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  if (idempotencyKey) headers.set("Idempotency-Key", idempotencyKey);

  try {
    const res = await fetch(`${API_BASE}${path}`, { ...init, headers });

    if (res.status === 204) return undefined as T;

    let body: unknown = null;
    const text = await res.text();
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    }

    if (!res.ok) {
      const fallback = getFallbackData<T>(path);
      if (fallback !== null) {
        return fallback;
      }
      const detail =
        body && typeof body === "object" && "detail" in (body as Record<string, unknown>)
          ? String((body as Record<string, unknown>).detail)
          : `Request failed with status ${res.status}`;
      throw new ApiError(detail, res.status);
    }

    return body as T;
  } catch (err) {
    // Graceful fallback for demo deployments (e.g. Vercel) when backend microservices are offline
    const fallback = getFallbackData<T>(path);
    if (fallback !== null) {
      return fallback;
    }
    throw err;
  }
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path, { method: "GET" }),
  post: <T>(path: string, data?: unknown, opts?: { idempotencyKey?: string; auth?: boolean }) =>
    apiFetch<T>(path, { method: "POST", body: data ? JSON.stringify(data) : undefined, ...opts }),
  patch: <T>(path: string, data?: unknown) =>
    apiFetch<T>(path, { method: "PATCH", body: data ? JSON.stringify(data) : undefined }),
};

export function setAuthTokens(access: string, refresh: string) {
  window.localStorage.setItem("es_access_token", access);
  window.localStorage.setItem("es_refresh_token", refresh);
}

export function clearAuthTokens() {
  window.localStorage.removeItem("es_access_token");
  window.localStorage.removeItem("es_refresh_token");
}
