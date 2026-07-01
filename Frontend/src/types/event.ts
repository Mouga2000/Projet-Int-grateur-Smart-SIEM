// src/types/event.ts

export type EventType = "LOGIN" | "NETWORK" | "FILE" | "PROCESS" | "AUTH" | "SYSTEM";

export interface SecurityEvent {
  id: string;
  type: EventType;
  timestamp: string;
  source: string;
  sourceIp?: string;
  destinationIp?: string;
  user?: string;
  description: string;
  rawLog?: string;
  hash?: string;         // SHA-256 pour vérification d'intégrité
  marked: boolean;
  alertId?: string;      // lié à une alerte si applicable
}

export interface TimelineEntry {
  event: SecurityEvent;
  relativeTime: number;  // ms depuis le premier événement
}