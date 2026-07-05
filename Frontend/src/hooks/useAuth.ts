// src/hooks/useAuth.ts
import { useAuthContext } from "../context/AuthContext";
import { hasAccess } from "../config/roles";
import type { Role } from "../config/roles";

export const useAuth = () => {
  const auth = useAuthContext();

  const canAccess = (page: string): boolean => {
    if (!auth.user) return false;
    return hasAccess(page, auth.user.role as Role);
  };

  const redirectPath = (): string => {
    if (!auth.user) return "/login";
    const defaults: Record<string, string> = {
      lecteur:        "/dashboard",
      analyste:       "/dashboard",
      auditeur:       "/audit/logs",
      rssi:           "/dashboard",
      administrateur: "/dashboard",
    };
    return defaults[auth.user.role] ?? "/dashboard";
  };

  return { ...auth, canAccess, redirectPath };
};