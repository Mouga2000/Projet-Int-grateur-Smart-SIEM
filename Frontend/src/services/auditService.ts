// src/services/auditService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";

interface AuditLog {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceId?: string;
  ip: string;
  timestamp: string;
  details?: Record<string, any>;
}

interface AuditFilter {
  userId?: string;
  action?: string;
  from?: string;
  to?: string;
  page?: number;
  size?: number;
}

const auditService = {
  getLogs: async (params: AuditFilter): Promise<{ items: AuditLog[]; total: number }> => {
    const { data } = await api.get(ENDPOINTS.logs.list, { params });
    return data;
  },

  verify: async (logId: string): Promise<{ valid: boolean; hash: string; computedHash: string }> => {
    const { data } = await api.post(ENDPOINTS.logs.detail(logId), { logId });
    return data;
  },

  export: async (params: AuditFilter): Promise<Blob> => {
    const exportEndpoint =
      ((ENDPOINTS.logs as unknown) as Record<string, string>)["export"] || "/logs/export";
    const { data } = await api.get(exportEndpoint, {
      params,
      responseType: "blob",
    });
    return data;
  },
};

export default auditService;