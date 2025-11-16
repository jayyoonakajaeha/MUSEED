"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';

interface AuthContextType {
  token: string | null;
  user: { username: string } | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<{ username: string } | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      try {
        const decodedUser: { sub: string, exp: number } = jwtDecode(storedToken);
        if (decodedUser.exp * 1000 > Date.now()) {
          setToken(storedToken);
          setUser({ username: decodedUser.sub });
        } else {
          // Token expired
          localStorage.removeItem('authToken');
        }
      } catch (error) {
        console.error("Failed to decode token on initial load", error);
        localStorage.removeItem('authToken');
      }
    }
  }, []);

  const login = (newToken: string) => {
    try {
      const decodedUser: { sub: string } = jwtDecode(newToken);
      localStorage.setItem('authToken', newToken);
      setToken(newToken);
      setUser({ username: decodedUser.sub });
    } catch (error) {
      console.error("Failed to decode token on login", error);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
