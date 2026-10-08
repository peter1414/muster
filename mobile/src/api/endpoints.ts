import { apiRequest } from './client';
import type {
  AuthResponse,
  DashboardResponse,
  EntriesResponse,
  ExerciseKey,
  LogEntry,
  StandardsResponse,
  User,
} from './types';

export function me() {
  return apiRequest<User>('/api/me');
}

export function register(username: string, email: string, password: string) {
  return apiRequest<AuthResponse>('/api/auth/register', {
    method: 'POST',
    body: { username, email, password },
    auth: false,
  });
}

export function login(username: string, password: string) {
  return apiRequest<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: { username, password },
    auth: false,
  });
}

export function forgotPassword(email: string) {
  return apiRequest<{ message: string }>('/api/auth/forgot-password', {
    method: 'POST',
    body: { email },
    auth: false,
  });
}

export function resetPassword(token: string, password: string) {
  return apiRequest<{ message: string }>('/api/auth/reset-password', {
    method: 'POST',
    body: { token, password },
    auth: false,
  });
}

export function deleteAccount() {
  return apiRequest<{ message: string }>('/api/auth/account', { method: 'DELETE' });
}

export function fetchStandards() {
  return apiRequest<StandardsResponse>('/api/standards', { auth: false });
}

export function fetchDashboard() {
  return apiRequest<DashboardResponse>('/api/dashboard');
}

export function fetchEntries(page = 1, perPage = 20, exercise?: ExerciseKey) {
  const params = new URLSearchParams({ page: String(page), per_page: String(perPage) });
  if (exercise) params.set('exercise', exercise);
  return apiRequest<EntriesResponse>(`/api/entries?${params.toString()}`);
}

export function createEntry(input: {
  exercise: ExerciseKey;
  value: number | string;
  entry_date?: string;
  notes?: string;
}) {
  return apiRequest<LogEntry>('/api/entries', { method: 'POST', body: input });
}

export function updateEntry(
  id: number,
  input: Partial<{
    exercise: ExerciseKey;
    value: number | string;
    entry_date: string;
    notes: string;
  }>
) {
  return apiRequest<LogEntry>(`/api/entries/${id}`, { method: 'PUT', body: input });
}

export function deleteEntry(id: number) {
  return apiRequest<{ message: string }>(`/api/entries/${id}`, { method: 'DELETE' });
}
