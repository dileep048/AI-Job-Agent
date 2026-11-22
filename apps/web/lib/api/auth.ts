import { apiRequest, clearTokens, setTokens } from "@/lib/api/client";
import type { TokenResponse, User } from "@/types/api";

export async function register(payload: {
  email: string;
  password: string;
  name?: string;
}): Promise<TokenResponse> {
  const tokens = await apiRequest<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: payload,
    auth: false,
  });
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

export async function login(payload: { email: string; password: string }): Promise<TokenResponse> {
  const tokens = await apiRequest<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: payload,
    auth: false,
  });
  setTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

export async function me(): Promise<User> {
  return apiRequest<User>("/api/v1/auth/me");
}

export function logout(): void {
  clearTokens();
}
