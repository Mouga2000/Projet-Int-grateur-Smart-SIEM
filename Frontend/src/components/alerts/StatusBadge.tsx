// src/components/alerts/StatusBadge.tsx
import type { AlertStatus, AlertSeverity } from "../../types/alert";

const STATUS_STYLES: Record<AlertStatus, string> = {
  ouverte:  "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-300 dark:border-blue-700",
  en_cours: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700",
  resolue:  "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 border-green-300 dark:border-green-700",
  classee:  "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400 border-gray-300 dark:border-gray-700",
};

const SEVERITY_STYLES: Record<AlertSeverity, string> = {
  critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400 border-red-300 dark:border-red-700",
  high:     "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400 border-orange-300 dark:border-orange-700",
  medium:   "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400 border-yellow-300 dark:border-yellow-700",
  low:      "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400 border-blue-300 dark:border-blue-700",
  info:     "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400 border-gray-300 dark:border-gray-700",
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
      className={`inline-flex items-center px-2 py-0.5 rounded text-xs border font-medium ${styles}`}
    >
      {value}
    </span>
  );
};

export default StatusBadge;
