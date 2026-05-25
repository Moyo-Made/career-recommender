import { createContext, useContext, useEffect, useState } from 'react';
import { getMe, loginUser, registerUser, TOKEN_KEY } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  // Only "loading" if there's a token to validate; otherwise we're done.
  const [loading, setLoading] = useState(() => !!localStorage.getItem(TOKEN_KEY));

  // On first load, restore the session from a saved token (if any).
  useEffect(() => {
    if (!localStorage.getItem(TOKEN_KEY)) return;
    getMe()
      .then((data) => setUser(data.user))
      .catch(() => localStorage.removeItem(TOKEN_KEY))
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password) {
    const data = await loginUser({ email, password });
    localStorage.setItem(TOKEN_KEY, data.token);
    setUser(data.user);
    return data.user;
  }

  async function register(name, email, password) {
    const data = await registerUser({ name, email, password });
    localStorage.setItem(TOKEN_KEY, data.token);
    setUser(data.user);
    return data.user;
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext);
}
