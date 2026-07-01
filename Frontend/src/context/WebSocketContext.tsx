// src/context/WebSocketContext.tsx
import { createContext, useContext, type ReactNode } from "react";
import { useWebSocket } from "../hooks/useWebSocket";

interface WebSocketContextType {
  send: (msg: { type: string; payload: any }) => void;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const WebSocketProvider = ({ children }: { children: ReactNode }) => {
  const { send } = useWebSocket({
    onMessage: () => {},  // Géré par AlertContext
    enabled: true,
  });

  return (
    <WebSocketContext.Provider value={{ send }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const ctx = useContext(WebSocketContext);
  if (!ctx) throw new Error("useWebSocketContext must be used inside <WebSocketProvider>");
  return ctx;
};