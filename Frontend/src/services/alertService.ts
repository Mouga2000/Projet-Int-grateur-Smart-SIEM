// src/services/alertService.ts
import api from "./api";
import type { Alert, AlertFilter, AlertStatus } from "../types/alert";

interface PaginatedAlerts {
  items: Alert[];
  total: number;
  page: number;
  size: number;
}

const alertService = {
  getAlerts: async (
    params: AlertFilter & { page?: number; size?: number }
  ): Promise<PaginatedAlerts> => {
    const query: Record<string, any> = { page: params.page ?? 1, size: params.size ?? 50 };
    if (params.severity) query.severity = params.severity;
    if (params.status) query.status = params.status;
    if (params.search) query.search = params.search;
    if (params.from) query.date_from = params.from;
    if (params.to) query.date_to = params.to;
    const { data } = await api.get("/alerts/", { params: query });
    return data;
  },

  getAlert: async (id: number): Promise<Alert> => {
    const { data } = await api.get(`/alerts/${id}`);
    return data;
  },

  updateStatus: async (id: number, status: AlertStatus): Promise<Alert> => {
    const { data } = await api.patch(`/alerts/${id}`, null, { params: { status } });
    return data;
  },
};

export default alertService;