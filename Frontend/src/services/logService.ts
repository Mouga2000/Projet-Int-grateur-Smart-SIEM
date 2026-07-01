// src/services/logService.ts
import api from "./api";
import { ENDPOINTS } from "../config/endpoints";
import type { LogEntry, LogListResponse, LogSearchRequest, TimelineResponse } from "../types/log";

const logService = {
  list: async (page = 1, size = 50): Promise<LogListResponse> => {
    const { data } = await api.get(ENDPOINTS.logs.list, { params: { page, size } });
    return data;
  },

  search: async (payload: LogSearchRequest): Promise<LogListResponse> => {
    const { data } = await api.post(ENDPOINTS.logs.search, payload);
    return data;
  },

  getById: async (id: string): Promise<LogEntry> => {
    const { data } = await api.get(ENDPOINTS.logs.detail(id));
    return data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(ENDPOINTS.logs.detail(id));
  },

  timeline: async (params: {
    interval?: string;
    date_from?: string;
    date_to?: string;
    severities?: string;
  }): Promise<TimelineResponse> => {
    const { data } = await api.get(ENDPOINTS.logs.timeline, { params });
    return data;
  },
};

export default logService;