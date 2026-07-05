// src/context/AuthContext.tsx
import { createContext, useContext, useState, useEffect, useMemo, useCallback, type ReactNode } from "react";
import type { AuthUser } from "../types/user";
import type { Role } from "../config/roles";
import authService from "../services/authService";
import userService from "../services/userService";

interface AuthContextType {
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string, mfa_code?: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (role: Role) => boolean;
  hasAnyRole: (roles: Role[]) => boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser]           = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) { setIsLoading(false); return; }

      try {
        const me = await userService.me();
        setUser({ ...me, access_token: token } as AuthUser);
      } catch {
        localStorage.clear();
      } finally {
        setIsLoading(false);
      }
    };
    init();
  }, []);

  const login = useCallback(async (username: string, password: string, mfa_code?: string) => {
    const result = await authService.login(username, password, mfa_code);

    localStorage.setItem("access_token", result.access_token);
    if (result.refresh_token) {
      localStorage.setItem("refresh_token", result.refresh_token);
    }

    setUser({
      id: result.user.id,
      username: result.user.username,
      email: result.user.email,
      role: result.user.role as Role,
      perimeter: result.user.perimeter as any,
      mfa_enabled: result.user.mfa_enabled,
      created_at: "",
      access_token: result.access_token,
    });
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
    localStorage.clear();
    window.location.href = "/login";
  }, []);

  const hasRole    = useCallback((role: Role)   => user?.role === role, [user]);
  const hasAnyRole = useCallback((roles: Role[]) => roles.some((r) => r === user?.role), [user]);

  const contextValue = useMemo(() => ({
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasRole,
    hasAnyRole,
  }), [user, isLoading, login, logout, hasRole, hasAnyRole]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = (): AuthContextType => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuthContext must be used inside <AuthProvider>");
  return ctx;
};