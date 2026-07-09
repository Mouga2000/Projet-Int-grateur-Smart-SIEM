// src/types/report.ts

export type ReportFormat = "PDF" | "CSV" | "EXCEL";
export type ReportType   = "SECURITY" | "AUDIT" | "KPI" | "INCIDENT";

export interface Report {
  id: string;
  type: ReportType;
  format: ReportFormat;
  title: string;
  generatedBy: string;
  generatedAt: string;
  period: { from: string; to: string };
  downloadUrl?: string;
}

export interface ReportConfig {
  type: ReportType;
  format: ReportFormat;
  period: { from: string; to: string };
  scheduled?: boolean;
  scheduleInterval?: "DAILY" | "WEEKLY" | "MONTHLY";
}