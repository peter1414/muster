import React, { createContext, useContext, useEffect, useState } from 'react';

import { fetchStandards } from '../api/endpoints';
import type { StandardsResponse } from '../api/types';

interface StandardsContextValue {
  data: StandardsResponse | null;
  isLoading: boolean;
  error: string | null;
  reload: () => void;
}

const StandardsContext = createContext<StandardsContextValue | undefined>(undefined);

export function StandardsProvider({ children }: { children: React.ReactNode }) {
  const [data, setData] = useState<StandardsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    fetchStandards()
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((e) => {
        if (!cancelled) setError(e.message ?? 'Failed to load standards.');
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  return (
    <StandardsContext.Provider
      value={{ data, isLoading, error, reload: () => setReloadKey((k) => k + 1) }}
    >
      {children}
    </StandardsContext.Provider>
  );
}

export function useStandards() {
  const ctx = useContext(StandardsContext);
  if (!ctx) throw new Error('useStandards must be used within a StandardsProvider');
  return ctx;
}
