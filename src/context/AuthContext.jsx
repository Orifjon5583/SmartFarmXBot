import { createContext, useContext, useMemo, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('greenhouse_user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async ({ email, password }) => {
    if (!email || password.length < 4) {
      throw new Error('Operator emaili va parolni to‘g‘ri kiriting.');
    }
    const session = { name: 'Issiqxona administratori', email, role: 'Raspberry Pi operatori' };
    localStorage.setItem('greenhouse_user', JSON.stringify(session));
    localStorage.setItem('greenhouse_token', `demo-token-${Date.now()}`);
    setUser(session);
    return session;
  };

  const logout = () => {
    localStorage.removeItem('greenhouse_user');
    localStorage.removeItem('greenhouse_token');
    setUser(null);
  };

  const value = useMemo(() => ({ user, login, logout, isAuthenticated: Boolean(user) }), [user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useAuth AuthProvider ichida ishlatilishi kerak');
  }
  return value;
}
