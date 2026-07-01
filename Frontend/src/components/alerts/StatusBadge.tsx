// src/components/alerts/StatusBadge.tsx
import type { AlertStatus, AlertSeverity } from "../../types/alert";

const STATUS_STYLES: Record<AlertStatus, string> = {
  NEW:          "bg-blue-900/40 text-blue-400 border-blue-800",
  ACKNOWLEDGED: "bg-yellow-900/40 text-yellow-400 border-yellow-800",
  IN_PROGRESS:  "bg-orange-900/40 text-orange-400 border-orange-800",
  ESCALATED:    "bg-red-900/40 text-red-400 border-red-800",
  RESOLVED:     "bg-green-900/40 text-green-400 border-green-800",
  CLOSED:       "bg-gray-800 text-gray-500 border-gray-700",
};

const SEVERITY_STYLES: Record<AlertSeverity, string> = {
  CRITICAL: "bg-red-900/60 text-red-300 border-red-700",
  HIGH:     "bg-orange-900/60 text-orange-300 border-orange-700",
  MEDIUM:   "bg-yellow-900/60 text-yellow-300 border-yellow-700",
  LOW:      "bg-blue-900/40 text-blue-300 border-blue-700",
  INFO:     "bg-gray-800 text-gray-400 border-gray-700",
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