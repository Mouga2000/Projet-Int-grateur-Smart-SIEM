// src/pages/alerts/AlertDetail.tsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { Alert } from "../../types/alert";
import alertService from "../../services/alertService";
import StatusBadge from "../../components/alerts/StatusBadge";
import { Button } from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../config/roles";

const AlertDetail = () => {
  const { id }     = useParams<{ id: string }>();
  const navigate   = useNavigate();
  const { hasAnyRole } = useAuth();
  const canEdit    = hasAnyRole([Role.ANALYSTE, Role.ADMINISTRATEUR]);

  const [alert, setAlert]               = useState<Alert | null>(null);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState<string | null>(null);
  const [saving, setSaving]             = useState(false);

  useEffect(() => {
    if (!id) return;
    alertService.getAlert(parseInt(id))
      .then(setAlert)
      .catch(() => setError("Alerte introuvable."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleStatus = async (status: Alert["status"]) => {
    if (!alert) return;
    setSaving(true);
    try {
      const updated = await alertService.updateStatus(Number(alert.id), status);
      setAlert(updated);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-sm text-muted-foreground">Chargement...</p>;
  if (error || !alert) return <p className="text-sm text-destructive">{error ?? "Erreur"}</p>;

  const fields: [string, string | undefined][] = [
    ["ID",            String(alert.id)],
    ["Titre",         alert.title],
    ["Description",   alert.description],
    ["Sévérité",      alert.severity],
    ["Statut",        alert.status],
    ["Hôte",          alert.host],
    ["IP source",     alert.source_ip],
    ["Règle",         alert.rule_id ? `#${alert.rule_id}` : undefined],
    ["Confiance",     alert.confidence ? `${alert.confidence}%` : undefined],
    ["Créée le",      alert.created_at ? new Date(alert.created_at).toLocaleString("fr-FR") : undefined],
  ];

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      {/* Breadcrumb */}
      <button
        onClick={() => navigate("/alerts")}
        className="self-start text-xs text-muted-foreground transition-colors hover:text-foreground"
      >
        ← Retour aux alertes
      </button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-lg font-semibold leading-snug text-foreground">{alert.title}</h1>
          <div className="flex gap-2">
            <StatusBadge type="severity" value={alert.severity} />
            <StatusBadge type="status"   value={alert.status}   />
          </div>
        </div>

        {canEdit && (
          <div className="flex gap-2 shrink-0">
            {alert.status === "ouverte" && (
              <Button
                variant="secondary"
                size="sm"
                disabled={saving}
                onClick={() => handleStatus("en_cours")}
              >
                {saving ? "..." : "Prendre en charge"}
              </Button>
            )}
            {alert.status === "en_cours" && (
              <Button
                size="sm"
                disabled={saving}
                onClick={() => handleStatus("resolue")}
              >
                {saving ? "..." : "Résoudre"}
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Description */}
      <div className="rounded-xl border border-border bg-card p-4 text-card-foreground">
        <p className="mb-2 text-xs text-muted-foreground">Description</p>
        <p className="text-sm leading-relaxed text-foreground">{alert.description}</p>
      </div>

      {/* Champs détaillés */}
      <div className="overflow-hidden rounded-xl border border-border bg-card text-card-foreground">
        <table className="w-full text-sm">
          <tbody>
            {fields
              .filter(([, val]) => val)
              .map(([label, val]) => (
                <tr key={label} className="border-b border-border last:border-0">
                  <td className="w-40 px-4 py-2.5 text-xs text-muted-foreground">{label}</td>
                  <td className="break-all px-4 py-2.5 font-mono text-xs text-foreground">{val}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Lien investigation */}
      <button
        onClick={() => navigate(`/investigations?alertId=${alert.id}`)}
        className="self-start text-xs text-primary transition-colors hover:text-primary/80"
      >
        → Investiguer cette alerte
      </button>
    </div>
  );
};

export default AlertDetail;
