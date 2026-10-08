import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import * as endpoints from '../api/endpoints';
import { setOnAuthExpired } from '../api/client';
import { clearTokens, getRefreshToken, saveTokens } from '../api/tokenStorage';
import type { User } from '../api/types';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean; // still checking for a persisted session on cold start
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(async () => {
    await clearTokens();
    setUser(null);
  }, []);

  // On cold start, if a refresh token is on-device, try to resume the
  // session by hitting a protected endpoint (which triggers the client's
  // built-in refresh-on-401 flow).
  useEffect(() => {
    setOnAuthExpired(() => setUser(null));

    (async () => {
      const refreshToken = await getRefreshToken();
      if (!refreshToken) {
        setIsLoading(false);
        return;
      }
      try {
        const currentUser = await endpoints.me();
        setUser(currentUser);
      } catch {
        await clearTokens();
      } finally {
        setIsLoading(false);
      }
    })();

    return () => setOnAuthExpired(null);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const res = await endpoints.login(username, password);
    await saveTokens(res.access_token, res.refresh_token);
    setUser(res.user);
  }, []);

  const registerFn = useCallback(
    async (username: string, email: string, password: string) => {
      const res = await endpoints.register(username, email, password);
      await saveTokens(res.access_token, res.refresh_token);
      setUser(res.user);
    },
    []
  );

  const deleteAccount = useCallback(async () => {
    await endpoints.deleteAccount();
    await clearTokens();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, isLoading, login, register: registerFn, logout, deleteAccount }),
    [user, isLoading, login, registerFn, logout, deleteAccount]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
