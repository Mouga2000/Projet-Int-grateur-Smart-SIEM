// src/pages/alerts/Alerts.tsx
import { useState } from "react";
import { useAlerts } from "../../hooks/useAlerts";
import AlertTable from "../../components/alerts/AlertTable";
import type { AlertSeverity, AlertStatus } from "../../types/alert";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../config/roles";
import { Card, CardContent } from "../../components/ui/card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Search } from "lucide-react";

const SEVERITIES: AlertSeverity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: AlertStatus[]     = ["ouverte", "en_cours", "resolue", "classee"];

const Alerts = () => {
  const { alerts, loading, error, total, page, setPage, filter, setFilter, refresh } = useAlerts();
  const { hasAnyRole } = useAuth();
  const isReadOnly = !hasAnyRole([Role.ANALYSTE, Role.ADMINISTRATEUR]);
  const pageSize = 20;
  const [dateError, setDateError] = useState("");
  const [draftFilter, setDraftFilter] = useState<Record<string, string>>({});

  const handleDraftChange = (key: string, value: string) => {
    const updated = { ...draftFilter, [key]: value || "" };
    setDraftFilter(updated);

    if (key === "from" || key === "to") {
      const fromVal = key === "from" ? value : draftFilter.from;
      const toVal = key === "to" ? value : draftFilter.to;
      if (fromVal && toVal && fromVal > toVal) {
        setDateError("La date de début ne peut pas être postérieure à la date de fin.");
      } else {
        setDateError("");
      }
    }
  };

  const applyFilters = () => {
    setDateError("");
    const f: any = {};
    if (draftFilter.severity) f.severity = draftFilter.severity;
    if (draftFilter.status) f.status = draftFilter.status;
    if (draftFilter.search) f.search = draftFilter.search;
    if (draftFilter.from) f.from = draftFilter.from;
    if (draftFilter.to) {
      if (draftFilter.from && draftFilter.from > draftFilter.to) {
        setDateError("La date de début ne peut pas être postérieure à la date de fin.");
        return;
      }
      f.to = draftFilter.to;
    }
    setFilter(f as any);
    setPage(1);
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white font-medium text-lg">Alertes</h1>
          <p className="text-white/60 text-sm">{total} alerte{total > 1 ? "s" : ""} au total</p>
        </div>
        <div className="flex items-center gap-3">
          <Button variant="outline" onClick={refresh}>↻ Actualiser</Button>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
            <select
              value={draftFilter.severity ?? ""}
              onChange={(e) => handleDraftChange("severity", e.target.value)}
              className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm text-white [&>option]:text-black"
            >
              <option value="">Toutes les sévérités</option>
              {SEVERITIES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <select
              value={draftFilter.status ?? ""}
              onChange={(e) => handleDraftChange("status", e.target.value)}
              className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm text-white [&>option]:text-black"
            >
              <option value="">Tous les statuts</option>
              {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>

            <Input
              placeholder="Rechercher..."
              value={draftFilter.search ?? ""}
              onChange={(e) => handleDraftChange("search", e.target.value)}
            />

            <Input
              type="datetime-local"
              value={draftFilter.from ?? ""}
              max={draftFilter.to || undefined}
              onChange={(e) => handleDraftChange("from", e.target.value)}
            />

            <Input
              type="datetime-local"
              value={draftFilter.to ?? ""}
              min={draftFilter.from || undefined}
              onChange={(e) => handleDraftChange("to", e.target.value)}
            />
          </div>

          <div className="flex items-center gap-3 mt-3">
            <Button size="sm" onClick={applyFilters}>
              <Search className="h-4 w-4 mr-1.5" />
              Appliquer les filtres
            </Button>
            <Button size="sm" variant="ghost" onClick={() => { setDraftFilter({}); setFilter({}); setPage(1); }}>
              Réinitialiser
            </Button>
            {dateError && <p className="text-red-400 text-xs">{dateError}</p>}
            {isReadOnly && <p className="text-white/50 text-xs">Mode lecture seule</p>}
          </div>
        </CardContent>
      </Card>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      <Card>
        <AlertTable alerts={alerts} loading={loading} />
      </Card>

      {total > pageSize && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-white/60">Page {page} / {Math.ceil(total / pageSize)}</span>
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
