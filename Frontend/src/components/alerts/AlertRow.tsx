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
      className="border-b border-border/40 hover:bg-muted/30 cursor-pointer transition-colors"
    >
      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">
        #{alert.id}
      </td>
      <td className="px-4 py-3 text-sm text-foreground max-w-xs truncate transition-colors">
        {alert.title}
      </td>
      <td className="px-4 py-3">
        <StatusBadge type="severity" value={alert.severity} />
      </td>
      <td className="px-4 py-3">
        <StatusBadge type="status" value={alert.status} />
      </td>
      <td className="px-4 py-3 text-xs text-muted-foreground">{alert.host || alert.source_ip || "—"}</td>
      <td className="px-4 py-3 text-xs font-mono text-muted-foreground">{alert.source_ip || "—"}</td>
      <td className="px-4 py-3 text-xs text-muted-foreground">
        {alert.created_at ? new Date(alert.created_at).toLocaleString("fr-FR") : "—"}
      </td>
    </tr>
  );
};

export default AlertRow;
