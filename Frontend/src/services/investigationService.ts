// src/services/investigationService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type {
  Investigation,
  InvestigationListResponse,
  CreateInvestigationPayload,
  InvestigationStatus,
} from "../types/investigation";

const investigationService = {
  list: async (params: { status?: InvestigationStatus; page?: number; size?: number }): Promise<InvestigationListResponse> => {
    const { data } = await api.get(ENDPOINTS.investigations.list, { params });
    return data;
  },

  create: async (payload: CreateInvestigationPayload): Promise<Investigation> => {
    const { data } = await api.post(ENDPOINTS.investigations.create, payload);
    return data;
  },

  getById: async (id: number): Promise<Investigation> => {
    const { data } = await api.get(ENDPOINTS.investigations.detail(id));
    return data;
  },

  addLog: async (id: number, log_id: string, note?: string, verdict?: string): Promise<any> => {
    const { data } = await api.post(ENDPOINTS.investigations.addLog(id), { log_id, note, verdict });
    return data;
  },

  updateStatus: async (id: number, status: InvestigationStatus, notes?: string): Promise<{ message: string }> => {
    const { data } = await api.patch(ENDPOINTS.investigations.status(id), null, {
      params: { status, notes },
    });
    return data;
  },

  update: async (id: number, payload: Partial<Investigation>): Promise<Investigation> => {
    const { data } = await api.patch(ENDPOINTS.investigations.update(id), payload);
    return data;
  },
};

export default investigationService;