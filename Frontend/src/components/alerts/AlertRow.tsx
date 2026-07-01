// src/components/alerts/AlertRow.tsx
import { useNavigate } from "react-router-dom";
import type { Alert } from "../../types/alert";
import StatusBadge from "./StatusBadge";

interface AlertRowProps {
  alert: Alert;
}

const AlertRow = ({ alert }: AlertRowProps) => {
  const navigate = useNavigate();

  return (
    <tr
      onClick={() => navigate(`/alerts/${alert.id}`)}
      className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/60 cursor-pointer transition-colors group"
    >
      <td className="px-4 py-3 text-xs text-gray-400 font-mono">
        {alert.id.slice(0, 8)}
      </td>
      <td className="px-4 py-3 text-sm text-gray-900 dark:text-white max-w-xs truncate group-hover:text-cyan-600 dark:group-hover:text-cyan-300 transition-colors">
        {alert.title}
      </td>
      <td className="px-4 py-3">
        <StatusBadge type="severity" value={alert.severity} />
      </td>
      <td className="px-4 py-3">
        <StatusBadge type="status" value={alert.status} />
      </td>
      <td className="px-4 py-3 text-xs text-gray-500">{alert.source}</td>
      <td className="px-4 py-3 text-xs text-gray-500">
        {new Date(alert.createdAt).toLocaleString("fr-FR")}
      </td>
    </tr>
  );
};

export default AlertRow;