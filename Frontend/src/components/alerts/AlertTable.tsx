// src/components/alerts/AlertTable.tsx
import type { Alert } from "../../types/alert";
import AlertRow from "./AlertRow";

interface AlertTableProps {
  alerts: Alert[];
  loading?: boolean;
}

const AlertTable = ({ alerts, loading }: AlertTableProps) => {
  if (loading) {
    return (
      <div className="py-12 text-center text-gray-500 text-sm">
        Chargement des alertes...
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="py-12 text-center text-gray-600 text-sm">
        Aucune alerte trouvée.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-900">
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">ID</th>
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">Titre</th>
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">Sévérité</th>
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">Statut</th>
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">Source</th>
            <th className="px-4 py-3 text-xs text-gray-600 dark:text-gray-300 font-medium">Date</th>
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