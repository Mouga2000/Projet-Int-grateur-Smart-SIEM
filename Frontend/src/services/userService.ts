// src/services/userService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type { User } from "../types/user";

const userService = {
  list: async (): Promise<User[]> => {
    const { data } = await api.get(ENDPOINTS.users.list);
    return data;
  },

  me: async (): Promise<User> => {
    const token = localStorage.getItem("access_token");
    if (token === "mock-token") {
      return {
        id: 1,
        username: "aloys",
        email: "aloys@siem.local",
        role: "administrateur" as any,
        perimeter: [],
        mfa_enabled: false,
        created_at: "",
      };
    }
    const { data } = await api.get(ENDPOINTS.users.me);
    return data;
  },

  create: async (payload: {
    username: string;
    email: string;
    password: string;
    role: string;
    perimeter: string[];
  }): Promise<User> => {
    const { data } = await api.post(ENDPOINTS.users.create, payload);
    return data;
  },

  updateRole: async (username: string, role: string): Promise<User> => {
    const { data } = await api.put(ENDPOINTS.users.updateRole(username), { role });
    return data;
  },

  updatePerimeter: async (username: string, perimeter: string[]): Promise<User> => {
    const { data } = await api.put(ENDPOINTS.users.updatePerimeter(username), { perimeter });
    return data;
  },
};

export default userService;