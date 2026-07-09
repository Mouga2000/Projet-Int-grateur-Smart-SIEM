// src/components/alerts/StatusBadge.tsx
import type { AlertStatus, AlertSeverity } from "../../types/alert";

const STATUS_STYLES: Record<AlertStatus, string> = {
  ouverte:  "bg-blue-500/10 text-blue-700 border-blue-200 dark:bg-blue-500/15 dark:text-blue-300 dark:border-blue-900/60",
  en_cours: "bg-yellow-500/10 text-yellow-700 border-yellow-200 dark:bg-yellow-500/15 dark:text-yellow-300 dark:border-yellow-900/60",
  resolue:  "bg-green-500/10 text-green-700 border-green-200 dark:bg-green-500/15 dark:text-green-300 dark:border-green-900/60",
  classee:  "bg-muted text-muted-foreground border-border",
};

const SEVERITY_STYLES: Record<AlertSeverity, string> = {
  critical: "bg-red-500/10 text-red-700 border-red-200 dark:bg-red-500/15 dark:text-red-300 dark:border-red-900/60",
  high:     "bg-orange-500/10 text-orange-700 border-orange-200 dark:bg-orange-500/15 dark:text-orange-300 dark:border-orange-900/60",
  medium:   "bg-yellow-500/10 text-yellow-700 border-yellow-200 dark:bg-yellow-500/15 dark:text-yellow-300 dark:border-yellow-900/60",
  low:      "bg-blue-500/10 text-blue-700 border-blue-200 dark:bg-blue-500/15 dark:text-blue-300 dark:border-blue-900/60",
  info:     "bg-muted text-muted-foreground border-border",
};

interface StatusBadgeProps {
  type: "status" | "severity";
  value: AlertStatus | AlertSeverity;
}

const StatusBadge = ({ type, value }: StatusBadgeProps) => {
  const styles =
    type === "status"
      ? STATUS_STYLES[value as AlertStatus]
      : SEVERITY_STYLES[value as AlertSeverity];

  return (
    <span
      className={`inline-flex items-center rounded border px-2 py-0.5 text-xs font-medium ${styles}`}
    >
      {value}
    </span>
  );
};

export default StatusBadge;
