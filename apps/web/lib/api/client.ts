const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  formData?: FormData;
};

const ACCESS_KEY = "aja_access_token";
const REFRESH_KEY = "aja_refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
  document.cookie = "aja_auth=1; path=/; SameSite=Lax";
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  document.cookie = "aja_auth=; path=/; max-age=0";
}

async function deflateError(response: Response): Promise<never> {
  let code = "HTTP_ERROR";
  let message = `Request failed (${response.status})`;
  try {
    const payload = (await response.json()) as { error?: { code?: string; message?: string } };
    code = payload.error?.code ?? code;
    message = payload.error?.message ?? message;
  } catch {
    // ignore non-JSON error bodies
  }
  if (response.status === 401) code = code || "UNAUTHORIZED";
  if (response.status === 403) code = code || "FORBIDDEN";
  if (response.status === 404) code = code || "NOT_FOUND";
  if (response.status === 422) code = code || "VALIDATION_ERROR";
  if (response.status >= 500) code = code || "INTERNAL_ERROR";
  throw new ApiError(response.status, code, message);
}

async function parseBody<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T;
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return (await response.json()) as T;
  }
  return (await response.arrayBuffer()) as T;
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
  retried = false,
): Promise<T> {
  const headers = new Headers();
  if (!options.formData) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth !== false) {
    const token = getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    method: options.method ?? "GET",
    headers,
    body: options.formData
      ? options.formData
      : options.body
        ? JSON.stringify(options.body)
        : undefined,
  });

  if (response.status === 401 && options.auth !== false && !retried) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return apiRequest<T>(path, options, true);
    }
    clearTokens();
    if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
      window.location.href = "/login";
    }
    await deflateError(response);
  }

  if (!response.ok) {
    await deflateError(response);
  }
  return parseBody<T>(response);
}

async function tryRefresh(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  const refresh = localStorage.getItem(REFRESH_KEY);
  if (!refresh) return false;
  const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });
  if (!response.ok) return false;
  const tokens = (await response.json()) as { access_token: string; refresh_token: string };
  setTokens(tokens.access_token, tokens.refresh_token);
  return true;
}

export function downloadUrl(path: string): string {
  return `${API_URL}${path}`;
}

export async function downloadAuthorized(path: string, filename: string): Promise<void> {
  const token = getAccessToken();
  const response = await fetch(`${API_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });
  if (!response.ok) {
    await deflateError(response);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}
