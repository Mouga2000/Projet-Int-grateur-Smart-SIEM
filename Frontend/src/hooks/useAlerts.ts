// src/hooks/useAlerts.ts
import { useState, useEffect, useCallback } from "react";
import type { Alert, AlertFilter } from "../types/alert";
import alertService from "../services/alertService";

interface UseAlertsReturn {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
  total: number;
  page: number;
  setPage: (p: number) => void;
  filter: AlertFilter;
  setFilter: (f: AlertFilter) => void;
  refresh: () => void;
  updateStatus: (id: string, status: Alert["status"]) => Promise<void>;
}

const PAGE_SIZE = 20;

export const useAlerts = (): UseAlertsReturn => {
  const [alerts, setAlerts]   = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const [total, setTotal]     = useState(0);
  const [page, setPage]       = useState(1);
  const [filter, setFilter]   = useState<AlertFilter>({});

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await alertService.getAlerts({ ...filter, page, size: PAGE_SIZE });
      setAlerts(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Erreur lors du chargement des alertes.");
    } finally {
      setLoading(false);
    }
  }, [filter, page]);

  useEffect(() => { fetchAlerts(); }, [fetchAlerts]);

  const updateStatus = async (id: string, status: Alert["status"]) => {
    await alertService.updateStatus(id, status);
    setAlerts((prev) =>
      prev.map((a) => (a.id === id ? { ...a, status } : a))
    );
  };

  return {
    alerts,
    loading,
    error,
    total,
    page,
    setPage,
    filter,
    setFilter: (f) => { setFilter(f); setPage(1); },
    refresh: fetchAlerts,
    updateStatus,
  };
};