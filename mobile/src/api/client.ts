import { API_BASE_URL } from '../config';
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
} from './tokenStorage';
import type { ApiErrorBody } from './types';

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

/** Called from AuthContext when a refresh fails, so the app can drop back to the login screen. */
let onAuthExpired: (() => void) | null = null;
export function setOnAuthExpired(cb: (() => void) | null) {
  onAuthExpired = cb;
}

let refreshInFlight: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshInFlight) return refreshInFlight;

  refreshInFlight = (async () => {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) return null;

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${refreshToken}` },
      });
      if (!res.ok) return null;
      const body = await res.json();
      await setAccessToken(body.access_token);
      return body.access_token as string;
    } catch {
      return null;
    } finally {
      refreshInFlight = null;
    }
  })();

  return refreshInFlight;
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  auth?: boolean; // default true
}

/**
 * Thin fetch wrapper: attaches the bearer token, retries once on 401 after
 * refreshing it, and normalizes error responses into ApiError.
 */
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options;

  const doFetch = async (token: string | null): Promise<Response> => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (auth && token) headers.Authorization = `Bearer ${token}`;

    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  };

  let token = auth ? await getAccessToken() : null;
  let res = await doFetch(token);

  if (auth && res.status === 401) {
    const newToken = await refreshAccessToken();
    if (newToken) {
      res = await doFetch(newToken);
    } else {
      await clearTokens();
      onAuthExpired?.();
      throw new ApiError('Session expired. Please log in again.', 401);
    }
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const errBody: ApiErrorBody = await res.json();
      message = errBody.error || errBody.message || message;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
