// src/types/archive.ts

export type ArchiveStatus = "certified" | "verified" | "compromised";

export interface Archive {
  id: number;
  date_from: string;
  date_to: string;
  log_count: number;
  chain_hash: string;
  previous_hash: string | null;
  status: ArchiveStatus;
  certified_at: string;
}

export interface ArchiveListResponse {
  items: Archive[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ArchiveChainEntry {
  id: number;
  period: string;
  logs: number;
  chain_hash: string;
  previous_hash: string;
  status: string;
  certified_at: string;
}

export interface VerifyResult {
  valid: boolean;
  details?: Record<string, any>;
}