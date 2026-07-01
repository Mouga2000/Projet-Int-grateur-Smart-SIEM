// src/context/AlertContext.tsx
import { createContext, useContext, useState, useCallback, type ReactNode} from "react";
import type { Alert } from "../types/alert";
import { useWebSocket } from "../hooks/useWebSocket";

interface AlertContextType {
  liveAlerts: Alert[];
  criticalCount: number;
  clearLive: () => void;
}

const AlertContext = createContext<AlertContextType | null>(null);

export const AlertProvider = ({ children }: { children: ReactNode }) => {
  const [liveAlerts, setLiveAlerts] = useState<Alert[]>([]);

  const handleMessage = useCallback((msg: { type: string; payload: any }) => {
    if (msg.type === "ALERT_NEW") {
      setLiveAlerts((prev) => [msg.payload as Alert, ...prev].slice(0, 100));
    }
    if (msg.type === "ALERT_UPDATED") {
      setLiveAlerts((prev) =>
        prev.map((a) => (a.id === msg.payload.id ? msg.payload : a))
      );
    }
  }, []);

  useWebSocket({ onMessage: handleMessage });

  const criticalCount = liveAlerts.filter(
    (a) => a.severity === "CRITICAL" && a.status === "NEW"
  ).length;

  return (
    <AlertContext.Provider value={{ liveAlerts, criticalCount, clearLive: () => setLiveAlerts([]) }}>
      {children}
    </AlertContext.Provider>
  );
};

export const useAlertContext = () => {
  const ctx = useContext(AlertContext);
  if (!ctx) throw new Error("useAlertContext must be used inside <AlertProvider>");
  return ctx;
};