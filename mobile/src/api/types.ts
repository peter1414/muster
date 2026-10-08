export type ExerciseKey = 'pushups' | 'situps' | 'pullups' | 'run_1_5mi' | 'swim_500m';

export interface StandardDef {
  label: string;
  unit: 'reps' | 'time';
  min: number;
  competitive: number;
  max: number;
  lower_better: boolean;
  min_display: string | number;
  competitive_display: string | number;
  max_display: string | number;
}

export interface StandardsResponse {
  exercise_order: ExerciseKey[];
  standards: Record<ExerciseKey, StandardDef>;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string | null;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
}

export interface LogEntry {
  id: number;
  exercise: ExerciseKey;
  label: string;
  value: number;
  display_value: string | number;
  entry_date: string; // YYYY-MM-DD
  notes: string;
  created_at: string | null;
}

export interface DashboardCard {
  key: ExerciseKey;
  label: string;
  unit: 'reps' | 'time';
  lower_better: boolean;
  min_display: string | number;
  competitive_display: string | number;
  max_display: string | number;
  entry: LogEntry | null;
  ratio?: number;
  tier?: 'below' | 'min' | 'competitive' | 'max';
}

export interface DashboardResponse {
  cards: DashboardCard[];
  total_entries: number;
}

export interface EntriesResponse {
  entries: LogEntry[];
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
}

export interface ApiErrorBody {
  error?: string;
  message?: string;
}
