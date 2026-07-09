// src/types/playbook.ts
// Types alignés avec le backend (SQLAlchemy) :
//   name, description, trigger, enabled, steps, variables,
//   timeout_seconds, max_retries, last_executed_at, execution_count, created_by

export type PlaybookTrigger = "manual" | "alert_created" | "alert_escalated" | "scheduled" | "webhook";

export interface PlaybookStep {
  action: "block_ip" | "disable_user" | "isolate_host" | "notify_slack" | "notify_email" | "create_ticket";
  params: Record<string, any>;
}

export interface Playbook {
  id: number;
  name: string;
  description: string | null;
  trigger: PlaybookTrigger;
  enabled: boolean;
  steps: PlaybookStep[];
  variables: Record<string, any>;
  timeout_seconds: number;
  max_retries: number;
  last_executed_at: string | null;
  execution_count: number;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}