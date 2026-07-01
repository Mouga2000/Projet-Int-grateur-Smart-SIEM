// src/types/investigation.ts

export type InvestigationStatus = "ouverte" | "en_cours" | "resolue" | "classee";
export type InvestigationSeverity = "low" | "medium" | "high" | "critical";
export type Verdict = "suspect" | "benign" | "confirmed" | "false_positive";

export interface Investigation {
  id: number;
  title: string;
  description?: string;
  severity: InvestigationSeverity;
  status: InvestigationStatus;
  tags: string[];
  mitre_tactic?: string;
  mitre_technique?: string;
  created_by: number;
  assigned_to?: number;
  created_at: string;
  updated_at?: string;
  logs?: any[];
}

export interface InvestigationListResponse {
  items: Investigation[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface CreateInvestigationPayload {
  title: string;
  description?: string;
  severity: InvestigationSeverity;
  tags: string[];
  log_ids: string[];
  mitre_tactic?: string;
  mitre_technique?: string;
}