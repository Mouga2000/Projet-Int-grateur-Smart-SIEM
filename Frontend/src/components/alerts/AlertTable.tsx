import type { Alert } from "../../types/alert";
import AlertRow from "./AlertRow";

interface AlertTableProps {
  alerts: Alert[];
  loading?: boolean;
}

const AlertTable = ({ alerts, loading }: AlertTableProps) => {
  if (loading) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Chargement des alertes...
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Aucune alerte trouvée.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg">
      <table className="w-full border-collapse text-left">
        <thead>
          <tr className="bg-muted/30">
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">ID</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Titre</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Sévérité</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Statut</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Hôte</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">IP source</th>
            <th className="px-4 py-3 text-xs font-medium text-muted-foreground">Date</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert) => (
            <AlertRow key={alert.id} alert={alert} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AlertTable;
