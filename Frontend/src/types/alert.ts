// src/types/alert.ts

export type AlertSeverity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "INFO";
export type AlertStatus   = "NEW" | "ACKNOWLEDGED" | "IN_PROGRESS" | "ESCALATED" | "RESOLVED" | "CLOSED";

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: AlertSeverity;
  status: AlertStatus;
  source: string;
  sourceIp?: string;
  destinationIp?: string;
  ruleId?: string;
  ruleName?: string;
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
  acknowledgedAt?: string;
  resolvedAt?: string;
}

export interface AlertFilter {
  severity?: AlertSeverity;
  status?: AlertStatus;
  source?: string;
  from?: string;
  to?: string;
  search?: string;
}