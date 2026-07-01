// src/services/authService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type { LoginResponse } from "../types/user";

const authService = {
  login: async (username: string, password: string, mfa_code?: string): Promise<LoginResponse> => {
    // Mock dev
    if (username === "aloys" && password === "1234") {
      return {
        access_token: "mock-token",
        refresh_token: null,
        user: {
          id: "1",
          username: "aloys",
          email: "aloys@siem.local",
          role: "administrateur" as any,
          perimeter: [],
          mfa_enabled: false,
          created_at: "",
        },
      } as any;
    }
    const { data } = await api.post(ENDPOINTS.auth.login, { username, password, mfa_code });
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post(ENDPOINTS.auth.logout).catch(() => {});
  },

  mfaStatus: async (): Promise<{ mfa_enabled: boolean }> => {
    const { data } = await api.get(ENDPOINTS.auth.mfaStatus);
    return data;
  },

  mfaSetup: async (): Promise<{ secret: string; uri: string; qr_code: string }> => {
    const { data } = await api.post(ENDPOINTS.auth.mfaSetup);
    return data;
  },

  mfaVerify: async (code: string): Promise<{ mfa_enabled: boolean }> => {
    const { data } = await api.post(ENDPOINTS.auth.mfaVerify, { code });
    return data;
  },

  mfaDisable: async (current_password: string): Promise<{ mfa_enabled: boolean }> => {
    const { data } = await api.post(ENDPOINTS.auth.mfaDisable, { current_password });
    return data;
  },
};

export default authService;