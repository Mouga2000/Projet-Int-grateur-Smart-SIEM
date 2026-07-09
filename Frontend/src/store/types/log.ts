// src/types/log.ts

export type Severity = "debug" | "info" | "warning" | "error" | "critical";

export interface LogEntry {
  id: string;
  timestamp: string;
  source_ip: string;
  host: string;
  log_type?: string;
  severity: Severity;
  raw_message: string;
  tags: string[];
}

export interface LogListResponse {
  items: LogEntry[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface LogSearchRequest {
  query?: string;
  source_ips?: string[];
  destination_ips?: string[];
  users?: string[];
  hosts?: string[];
  log_types?: string[];
  severities?: string[];
  tags?: string[];
  date_from?: string;
  date_to?: string;
  page?: number;
  size?: number;
}

export interface TimelineBucket {
  timestamp: string;
  count: number;
}

export interface TimelineResponse {
  timeline: TimelineBucket[];
  total: number;
  interval: string;
  bucket_count: number;
}