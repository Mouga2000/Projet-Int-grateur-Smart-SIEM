// src/types/playbook.ts

export type PlaybookMode    = "AUTO" | "CONFIRM";
export type PlaybookStatus  = "ACTIVE" | "INACTIVE" | "DRAFT";
export type PlaybookTrigger = "ALERT_CRITICAL" | "ALERT_HIGH" | "LOGIN_FAILED" | "ANOMALY" | "CUSTOM";

export interface PlaybookAction {
  id: string;
  order: number;
  name: string;
  type: "BLOCK_IP" | "ISOLATE_HOST" | "NOTIFY" | "CREATE_TICKET" | "RUN_SCRIPT";
  params: Record<string, string>;
}

export interface Playbook {
  id: string;
  name: string;
  description: string;
  trigger: PlaybookTrigger;
  mode: PlaybookMode;
  status: PlaybookStatus;
  actions: PlaybookAction[];
  createdAt: string;
  updatedAt: string;
}