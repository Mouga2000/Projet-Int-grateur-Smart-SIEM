// src/types/alert.ts

export type AlertSeverity = "info" | "low" | "medium" | "high" | "critical";
export type AlertStatus   = "ouverte" | "en_cours" | "resolue" | "classee";

export interface Alert {
  id: number;
  rule_id?: number;
  title: string;
  description?: string;
  severity: AlertSeverity;
  source_ip?: string;
  host?: string;
  status: AlertStatus;
  confidence?: number;
  mitre?: Record<string, any>;
  created_at?: string;
}

export interface AlertFilter {
  severity?: AlertSeverity;
  status?: AlertStatus;
  search?: string;
  from?: string;
  to?: string;
}
