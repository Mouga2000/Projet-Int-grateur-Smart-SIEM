// src/services/adminService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";

const adminService = {
  purgeLogs: async (days: number): Promise<{ deleted: number; retention_days: number; message: string }> => {
    const { data } = await api.post(ENDPOINTS.admin.purgeLogs, null, { params: { days } });
    return data;
  },

  purgeAudit: async (days: number): Promise<{ deleted: number; retention_days: number; message: string }> => {
    const { data } = await api.post(ENDPOINTS.admin.purgeAudit, null, { params: { days } });
    return data;
  },

  getRetentionConfig: async (): Promise<{ log_retention_days: number; audit_retention_days: number; next_purge: string }> => {
    const { data } = await api.get(ENDPOINTS.admin.retention);
    return data;
  },
};

export default adminService;