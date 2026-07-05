// src/types/investigation.ts

export type InvestigationStatus = "ouverte" | "en_cours" | "resolue" | "classee";
export type InvestigationSeverity = "low" | "medium" | "high" | "critical";
export type Verdict = "suspect" | "benign" | "confirmed" | "false_positive";

export interface InvestigationLog {
  id: number;
  log_id: string;
  log_index?: string;
  note?: string;
  verdict?: Verdict;
  added_by?: number;
  created_at: string;
  /** Présent quand le détail est chargé avec le log ES */
  log?: {
    id: string;
    timestamp: string;
    source_ip: string;
    host: string;
    severity: string;
    raw_message: string;
  };
}

export interface Investigation {
  id: number;
  title: string;
  description?: string;
  severity: InvestigationSeverity;
  status: InvestigationStatus;
  tags: string[];
  log_ids: string[];
  mitre_tactic?: string;
  mitre_technique?: string;
  created_by: number;
  assigned_to?: number;
  closed_at?: string;
  resolution_notes?: string;
  created_at: string;
  updated_at?: string;
  logs?: InvestigationLog[];
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
