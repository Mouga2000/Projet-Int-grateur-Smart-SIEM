// src/services/reportService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type { Report, ReportConfig } from "../types/report";

const reportsEndpoints = (ENDPOINTS as any).reports;

const reportService = {
  generate: async (config: ReportConfig): Promise<Report> => {
    const { data } = await api.post(reportsEndpoints.generate, config);
    return data;
  },

  export: async (config: ReportConfig): Promise<Blob> => {
    const { data } = await api.post(reportsEndpoints.export, config, {
      responseType: "blob",
    });
    return data;
  },

  schedule: async (config: ReportConfig): Promise<void> => {
    await api.post(reportsEndpoints.schedule, config);
  },

  list: async (): Promise<Report[]> => {
    const { data } = await api.get(reportsEndpoints.generate);
    return data;
  },
};

export default reportService;