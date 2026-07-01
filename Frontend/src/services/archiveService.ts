// src/services/archiveService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type { Archive, ArchiveListResponse, ArchiveChainEntry, VerifyResult } from "../types/archive";

const archiveService = {
  create: async (days: number, window_days: number): Promise<Archive> => {
    const { data } = await api.post(ENDPOINTS.archive.create, null, { params: { days, window_days } });
    return data;
  },

  list: async (page = 1, size = 50): Promise<ArchiveListResponse> => {
    const { data } = await api.get(ENDPOINTS.archive.list, { params: { page, size } });
    return data;
  },

  getChain: async (): Promise<{ chain: ArchiveChainEntry[]; length: number; integrity: string }> => {
    const { data } = await api.get(ENDPOINTS.archive.chain);
    return data;
  },

  verify: async (id: number): Promise<VerifyResult> => {
    const { data } = await api.post(ENDPOINTS.archive.verify(id));
    return data;
  },

  getById: async (id: number): Promise<Archive> => {
    const { data } = await api.get(ENDPOINTS.archive.detail(id));
    return data;
  },

  export: async (id: number): Promise<any> => {
    const { data } = await api.get(ENDPOINTS.archive.export(id));
    return data;
  },
};

export default archiveService;