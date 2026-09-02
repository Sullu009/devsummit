"use client";

import { createContext, useContext, useEffect, useState, ReactNode, useCallback } from "react";
import { api, clearAuthTokens, setAuthTokens } from "./api";
import type { AuthResponse, User, UserRole } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  register: (email: string, fullName: string, password: string, role: UserRole) => Promise<User>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    const token = typeof window !== "undefined" ? window.localStorage.getItem("es_access_token") : null;
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await api.get<User>("/auth/me");
      setUser(me);
    } catch {
      clearAuthTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.post<AuthResponse>("/auth/login", { email, password }, { auth: false });
    setAuthTokens(res.access_token, res.refresh_token);
    setUser(res.user);
    return res.user;
  }, []);

  const register = useCallback(async (email: string, fullName: string, password: string, role: UserRole) => {
    const res = await api.post<AuthResponse>("/auth/register", { email, full_name: fullName, password, role }, { auth: false });
    setAuthTokens(res.access_token, res.refresh_token);
    setUser(res.user);
    return res.user;
  }, []);

  const logout = useCallback(() => {
    clearAuthTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
