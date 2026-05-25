import { createContext, useCallback, useContext, useState } from 'react';
import { getHistory } from '../api';
import { useAuth } from '../auth/AuthContext';

// Session-level cache for the user's assessment history. Without this each
// visit to the Dashboard remounts the component, refetching from scratch and
// flashing a spinner. Caching here lets revisits render instantly.
const HistoryContext = createContext(null);

export function HistoryProvider({ children }) {
  const { user } = useAuth();
  // Stable per-user key so a cache from one account never bleeds into another.
  const userKey = user?.id ?? user?.email ?? null;

  // cache.items: null = not loaded yet; [] = loaded, no assessments.
  const [cache, setCache] = useState({ userKey: null, items: null });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // The cache only counts if it belongs to the current user; otherwise it
  // reads as empty (a miss), so login/logout/switch transparently resets it.
  const history = cache.userKey === userKey ? cache.items : null;

  const refresh = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getHistory();
      setCache({ userKey, items: data.history || [] });
    } catch {
      setError('We were unable to load your history. Please try again in a moment.');
    } finally {
      setLoading(false);
    }
  }, [userKey]);

  // Drop the cache so the next read refetches (e.g. after a new assessment).
  const invalidate = useCallback(() => setCache({ userKey: null, items: null }), []);

  return (
    <HistoryContext.Provider value={{ history, loading, error, refresh, invalidate }}>
      {children}
    </HistoryContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useHistory() {
  return useContext(HistoryContext);
}
