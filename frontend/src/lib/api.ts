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
    const detail =
      body && typeof body === "object" && "detail" in (body as Record<string, unknown>)
        ? String((body as Record<string, unknown>).detail)
        : `Request failed with status ${res.status}`;
    throw new ApiError(detail, res.status);
  }

  return body as T;
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path, { method: "GET" }),
  post: <T>(path: string, data?: unknown, opts?: { idempotencyKey?: string; auth?: boolean }) =>
    apiFetch<T>(path, { method: "POST", body: data ? JSON.stringify(data) : undefined, ...opts }),
  patch: <T>(path: string, data?: unknown) => apiFetch<T>(path, { method: "PATCH", body: data ? JSON.stringify(data) : undefined }),
};

export function setAuthTokens(access: string, refresh: string) {
  window.localStorage.setItem("es_access_token", access);
  window.localStorage.setItem("es_refresh_token", refresh);
}

export function clearAuthTokens() {
  window.localStorage.removeItem("es_access_token");
  window.localStorage.removeItem("es_refresh_token");
}
