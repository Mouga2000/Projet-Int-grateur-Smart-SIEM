// src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from "react";
import { ENDPOINTS } from "../config/endpoints";

type WsMessage = {
  type: string;
  payload: any;
};

interface UseWebSocketOptions {
  onMessage: (msg: WsMessage) => void;
  enabled?: boolean;
}

export const useWebSocket = ({ onMessage, enabled = true }: UseWebSocketOptions) => {
  const wsRef         = useRef<WebSocket | null>(null);
  const reconnectRef  = useRef<ReturnType<typeof setTimeout> | null>(null);
  const onMessageRef  = useRef(onMessage);

  // Garder la ref à jour sans recréer la connexion
  useEffect(() => { onMessageRef.current = onMessage; }, [onMessage]);

  const connect = useCallback(() => {
    if (!enabled) return;

    const token = localStorage.getItem("access_token");
    const wsBaseUrl = (ENDPOINTS as any).ws?.alerts;
    if (!wsBaseUrl) return; // WebSocket non configuré

    const ws = new WebSocket(`${wsBaseUrl}?token=${token}`);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      try {
        const msg: WsMessage = JSON.parse(e.data);
        onMessageRef.current(msg);
      } catch {
        // message non JSON ignoré
      }
    };

    ws.onclose = () => {
      // Reconnexion auto après 3s
      reconnectRef.current = setTimeout(() => connect(), 3000);
    };

    ws.onerror = () => ws.close();
  }, [enabled]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [connect]);

  const send = useCallback((msg: WsMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg));
    }
  }, []);

  return { send };
};