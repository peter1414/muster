export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

import type { LogEntry } from '../api/types';

export type AppStackParamList = {
  Dashboard: undefined;
  LogEntry: { editingEntry?: LogEntry } | undefined;
  History: undefined;
  Settings: undefined;
};
