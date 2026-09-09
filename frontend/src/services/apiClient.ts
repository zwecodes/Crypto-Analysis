import { env } from "../config/env";
import { supabase } from "../lib/supabaseClient";
import type { ApiErrorBody } from "../types/api";

/**
 * Error type thrown by apiRequest for any non-2xx response, matching
 * the error format defined in docs/api-contract.md:
 *   { "error": { "code": "...", "message": "..." } }
 */
export class ApiError extends Error {
  code: string;
  status: number;

  constructor(message: string, code: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

interface RequestOptions {
  method?: "GET" | "POST" | "DELETE" | "PUT" | "PATCH";
  body?: unknown;
  /** Attach the current Supabase session's JWT as a Bearer token. Defaults to true. */
  requiresAuth?: boolean;
}

/**
 * Thin fetch wrapper for the backend defined in docs/api-contract.md.
 * No feature logic lives here yet — this is just the shared plumbing
 * (base URL, JSON handling, auth header, error shape) that feature
 * services will be built on top of in later milestones.
 */
export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", body, requiresAuth = true } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (requiresAuth) {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (session?.access_token) {
      headers["Authorization"] = `Bearer ${session.access_token}`;
    }
  }

  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorBody = data as ApiErrorBody | null;
    throw new ApiError(
      errorBody?.error?.message ?? "Request failed",
      errorBody?.error?.code ?? "UNKNOWN_ERROR",
      response.status
    );
  }

  return data as T;
}
