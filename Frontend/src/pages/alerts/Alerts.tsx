// src/pages/alerts/Alerts.tsx
import { useState } from "react";
import { useAlerts } from "../../hooks/useAlerts";
import AlertTable from "../../components/alerts/AlertTable";
import type { AlertSeverity, AlertStatus } from "../../types/alert";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../config/roles";
import Card from "../../ui/kit/Card";
import Input from "../../ui/kit/Input";
import Select from "../../ui/kit/Select";
import Button from "../../ui/kit/Button";

const SEVERITIES: AlertSeverity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"];
const STATUSES: AlertStatus[]     = ["NEW", "ACKNOWLEDGED", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"];

const Alerts = () => {
  const { alerts, loading, error, total, page, setPage, filter, setFilter, refresh } = useAlerts();
  const { hasAnyRole } = useAuth();
  const isReadOnly = !hasAnyRole([Role.ANALYSTE, Role.ADMIN]);
  const pageSize = 20;

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-gray-900 dark:text-white font-medium text-lg">Alertes</h1>
          <p className="text-gray-500 text-sm">{total} alerte{total > 1 ? "s" : ""} au total</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={refresh}>↻ Actualiser</Button>
        </div>
      </div>

      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <Select value={filter.severity ?? ""} onChange={(e) => setFilter({ ...filter, severity: (e.target.value as AlertSeverity) || undefined })}>
            <option value="">Toutes les sévérités</option>
            {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
          </Select>

          <Select value={filter.status ?? ""} onChange={(e) => setFilter({ ...filter, status: (e.target.value as AlertStatus) || undefined })}>
            <option value="">Tous les statuts</option>
            {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
          </Select>

          <Input
            placeholder="Rechercher..."
            value={filter.search ?? ""}
            onChange={(e) => setFilter({ ...filter, search: e.target.value || undefined })}
          />

          <div className="flex gap-2">
            <Input type="datetime-local" value={filter.from ?? ""} onChange={(e) => setFilter({ ...filter, from: e.target.value || undefined })} />
            <Input type="datetime-local" value={filter.to ?? ""} onChange={(e) => setFilter({ ...filter, to: e.target.value || undefined })} />
          </div>
        </div>

        {isReadOnly && (
          <p className="text-xs text-gray-500 mt-2">Mode lecture seule</p>
        )}
      </Card>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      <Card>
        <AlertTable alerts={alerts} loading={loading} />
      </Card>

      {/* Pagination */}
      {total > pageSize && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">
            Page {page} / {Math.ceil(total / pageSize)}
          </span>
          <div className="flex gap-2">
            <Button variant="ghost" disabled={page === 1} onClick={() => setPage(page - 1)}>← Précédent</Button>
            <Button variant="ghost" disabled={page >= Math.ceil(total / pageSize)} onClick={() => setPage(page + 1)}>Suivant →</Button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alerts;