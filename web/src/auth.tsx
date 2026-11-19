import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { TOKEN_KEY, getMe, login as apiLogin, register as apiRegister, type Role, type User } from './api';

type Auth = {
  token: string | null;
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  /** UI only: hides what a role cannot do. The API remains the only enforcer of rights (FR-02). */
  can: (...roles: Role[]) => boolean;
};

const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState<User | null>(null);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (!token) return;
    getMe().then(setUser).catch(logout); // expired or revoked token: back to anonymous
  }, [token, logout]);

  const login = async (email: string, password: string) => {
    const { access_token } = await apiLogin(email, password);
    localStorage.setItem(TOKEN_KEY, access_token);
    setUser(await getMe());
    setToken(access_token);
  };
  const register = async (email: string, password: string) => {
    await apiRegister(email, password);
    await login(email, password);
  };
  const can = (...roles: Role[]) => user !== null && roles.includes(user.role);

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout, can }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): Auth {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
