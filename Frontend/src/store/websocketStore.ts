// src/store/websocketStore.ts
import { create } from "zustand";
import type { Alert } from "../types/alert";

interface WebSocketStore {
  connected: boolean;
  lastPing: number | null;
  liveAlerts: Alert[];
  setConnected: (v: boolean) => void;
  setLastPing: () => void;
  pushAlert: (alert: Alert) => void;
  updateAlert: (alert: Alert) => void;
  reset: () => void;
}

export const useWebSocketStore = create<WebSocketStore>((set) => ({
  connected:  false,
  lastPing:   null,
  liveAlerts: [],

  setConnected: (v) => set({ connected: v }),
  setLastPing:  ()  => set({ lastPing: Date.now() }),

  pushAlert: (alert) =>
    set((state) => ({
      liveAlerts: [alert, ...state.liveAlerts].slice(0, 100),
    })),

  updateAlert: (alert) =>
    set((state) => ({
      liveAlerts: state.liveAlerts.map((a) => (a.id === alert.id ? alert : a)),
    })),

  reset: () => set({ connected: false, lastPing: null, liveAlerts: [] }),
}));