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

  if (loading) return <p className="text-gray-500 text-sm">Chargement...</p>;
  if (error || !alert) return <p className="text-red-400 text-sm">{error ?? "Erreur"}</p>;

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
        className="text-xs text-gray-500 hover:text-gray-300 transition-colors self-start"
      >
        ← Retour aux alertes
      </button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-2">
          <h1 className="text-white font-medium text-lg leading-snug">{alert.title}</h1>
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
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <p className="text-xs text-gray-500 mb-2">Description</p>
        <p className="text-sm text-gray-200 leading-relaxed">{alert.description}</p>
      </div>

      {/* Champs détaillés */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-sm">
          <tbody>
            {fields
              .filter(([, val]) => val)
              .map(([label, val]) => (
                <tr key={label} className="border-b border-gray-800 last:border-0">
                  <td className="px-4 py-2.5 text-gray-500 w-40 text-xs">{label}</td>
                  <td className="px-4 py-2.5 text-gray-200 font-mono text-xs break-all">{val}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Lien investigation */}
      <button
        onClick={() => navigate(`/investigations?alertId=${alert.id}`)}
        className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors self-start"
      >
        → Investiguer cette alerte
      </button>
    </div>
  );
};

export default AlertDetail;