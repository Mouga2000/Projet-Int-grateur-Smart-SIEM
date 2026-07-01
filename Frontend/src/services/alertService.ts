// src/services/alertService.ts
import api from "./api";
import type { Alert, AlertFilter, AlertStatus } from "../types/alert";

interface PaginatedAlerts {
  items: Alert[];
  total: number;
  page: number;
  size: number;
}

const ALERT_ENDPOINTS = {
  list: "/alerts",
  detail: (id: string) => `/alerts/${id}`,
  status: (id: string) => `/alerts/${id}/status`,
  escalate: (id: string) => `/alerts/${id}/escalate`,
};

const alertService = {
  getAlerts: async (
    params: AlertFilter & { page?: number; size?: number }
  ): Promise<PaginatedAlerts> => {
    const { data } = await api.get(ALERT_ENDPOINTS.list, { params });
    return data;
  },

  getAlert: async (id: string): Promise<Alert> => {
    const { data } = await api.get(ALERT_ENDPOINTS.detail(id));
    return data;
  },

  updateStatus: async (id: string, status: AlertStatus): Promise<Alert> => {
    const { data } = await api.patch(ALERT_ENDPOINTS.status(id), { status });
    return data;
  },

  escalate: async (id: string, reason: string): Promise<Alert> => {
    const { data } = await api.post(ALERT_ENDPOINTS.escalate(id), { reason });
    return data;
  },
};

export default alertService;