// src/pages/alerts/AlertDetail.tsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { Alert } from "../../types/alert";
import alertService from "../../services/alertService";
import StatusBadge from "../../components/alerts/StatusBadge";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../config/roles";

const AlertDetail = () => {
  const { id }     = useParams<{ id: string }>();
  const navigate   = useNavigate();
  const { hasAnyRole } = useAuth();
  const canEdit    = hasAnyRole([Role.ANALYSTE, Role.ADMIN]);

  const [alert, setAlert]               = useState<Alert | null>(null);
  const [loading, setLoading]           = useState(true);
  const [error, setError]               = useState<string | null>(null);
  const [escalateOpen, setEscalateOpen] = useState(false);
  const [escalateReason, setEscalateReason] = useState("");
  const [saving, setSaving]             = useState(false);

  useEffect(() => {
    if (!id) return;
    alertService.getAlert(id)
      .then(setAlert)
      .catch(() => setError("Alerte introuvable."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleStatus = async (status: Alert["status"]) => {
    if (!alert) return;
    setSaving(true);
    try {
      const updated = await alertService.updateStatus(alert.id, status);
      setAlert(updated);
    } finally {
      setSaving(false);
    }
  };

  const handleEscalate = async () => {
    if (!alert) return;
    setSaving(true);
    try {
      const updated = await alertService.escalate(alert.id, escalateReason);
      setAlert(updated);
      setEscalateOpen(false);
      setEscalateReason("");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="text-gray-500 text-sm">Chargement...</p>;
  if (error || !alert) return <p className="text-red-400 text-sm">{error ?? "Erreur"}</p>;

  const fields: [string, string | undefined][] = [
    ["ID",            alert.id],
    ["Source",        alert.source],
    ["IP source",     alert.sourceIp],
    ["IP destination",alert.destinationIp],
    ["Règle",         alert.ruleName],
    ["Assigné à",     alert.assignedTo],
    ["Créée le",      new Date(alert.createdAt).toLocaleString("fr-FR")],
    ["Mise à jour",   new Date(alert.updatedAt).toLocaleString("fr-FR")],
    ["Accusée le",    alert.acknowledgedAt ? new Date(alert.acknowledgedAt).toLocaleString("fr-FR") : undefined],
    ["Résolue le",    alert.resolvedAt ? new Date(alert.resolvedAt).toLocaleString("fr-FR") : undefined],
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
            {alert.status === "NEW" && (
              <Button
                variant="secondary"
                size="sm"
                loading={saving}
                onClick={() => handleStatus("ACKNOWLEDGED")}
              >
                Accuser réception
              </Button>
            )}
            {alert.status === "ACKNOWLEDGED" && (
              <Button
                variant="secondary"
                size="sm"
                loading={saving}
                onClick={() => handleStatus("IN_PROGRESS")}
              >
                Prendre en charge
              </Button>
            )}
            {["NEW", "ACKNOWLEDGED", "IN_PROGRESS"].includes(alert.status) && (
              <Button
                variant="danger"
                size="sm"
                onClick={() => setEscalateOpen(true)}
              >
                Escalader
              </Button>
            )}
            {alert.status === "IN_PROGRESS" && (
              <Button
                variant="primary"
                size="sm"
                loading={saving}
                onClick={() => handleStatus("RESOLVED")}
              >
                Résoudre
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
        onClick={() => navigate(`/investigation?alertId=${alert.id}`)}
        className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors self-start"
      >
        → Investiguer cette alerte
      </button>

      {/* Modal escalade */}
      <Modal
        open={escalateOpen}
        onClose={() => setEscalateOpen(false)}
        title="Escalader l'alerte"
        size="sm"
      >
        <div className="flex flex-col gap-4">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Motif d'escalade</label>
            <textarea
              rows={4}
              value={escalateReason}
              onChange={(e) => setEscalateReason(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500 resize-none"
              placeholder="Décrivez la raison de l'escalade..."
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button variant="ghost" size="sm" onClick={() => setEscalateOpen(false)}>
              Annuler
            </Button>
            <Button
              variant="danger"
              size="sm"
              loading={saving}
              disabled={!escalateReason.trim()}
              onClick={handleEscalate}
            >
              Confirmer l'escalade
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default AlertDetail;