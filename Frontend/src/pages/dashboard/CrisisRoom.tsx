// src/pages/dashboard/CrisisRoom.tsx
import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAlertContext } from "../../context/AlertContext";
import type { Alert } from "../../types/alert";
import StatusBadge from "../../components/alerts/StatusBadge";
import api from "../../services/api";

const CrisisRoom = () => {
  const navigate = useNavigate();
  const { liveAlerts } = useAlertContext();
  const [criticals, setCriticals] = useState<Alert[]>([]);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchCriticals = useCallback(async () => {
    try {
      const { data } = await api.get("/alerts", {
        params: { severity: "critical", size: 50 },
      });
      setCriticals(data.items);
      setLastRefresh(new Date());
    } catch {}
  }, []);

  // Refresh auto toutes les 5s
  useEffect(() => {
    fetchCriticals();
    const interval = setInterval(fetchCriticals, 5000);
    return () => clearInterval(interval);
  }, [fetchCriticals]);

  // Fusionner avec les alertes live
  const allCriticals = [
    ...liveAlerts.filter((a) => a.severity === "critical"),
    ...criticals,
  ].filter(
    (a, i, arr) => arr.findIndex((x) => x.id === a.id) === i
  );

  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Header plein écran */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <h1 className="text-white font-medium text-lg tracking-wide">
            CRISIS ROOM
          </h1>
          <span className="text-gray-600 text-xs font-mono">
            — LIVE
          </span>
        </div>
        <div className="text-xs text-gray-500 font-mono">
          Dernière maj : {lastRefresh.toLocaleTimeString("fr-FR")}
        </div>
      </div>

      {/* Compteur critique */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-red-950/40 border border-red-900 rounded-xl p-4 col-span-1">
          <p className="text-xs text-red-500 mb-1">Alertes critiques actives</p>
          <p className="text-4xl font-bold text-red-400">
            {allCriticals.filter((a) => a.status === "ouverte").length}
          </p>
        </div>
        <div className="bg-orange-950/40 border border-orange-900 rounded-xl p-4">
          <p className="text-xs text-orange-500 mb-1">En cours de traitement</p>
          <p className="text-4xl font-bold text-orange-400">
            {allCriticals.filter((a) => a.status === "en_cours").length}
          </p>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p className="text-xs text-gray-500 mb-1">Résolues</p>
          <p className="text-4xl font-bold text-white">
            {allCriticals.filter((a) => a.status === "resolue").length}
          </p>
        </div>
      </div>

      {/* Liste des alertes critiques */}
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-2">
          {allCriticals.length === 0 && (
            <div className="py-12 text-center text-gray-600 text-sm">
              Aucune alerte critique active.
            </div>
          )}
          {allCriticals.map((alert) => (
            <div
              key={alert.id}
              className="bg-gray-900 border border-red-900/40 rounded-lg p-4 flex items-start justify-between gap-4 cursor-pointer hover:border-red-500/60 transition-colors"
              onClick={() => navigate(`/alerts/${alert.id}`)}
            >
              <div className="flex flex-col gap-1 min-w-0">
                <p className="text-sm text-white font-medium truncate">
                  {alert.title}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {alert.host || alert.source_ip || "—"}
                  {alert.source_ip && ` · ${alert.source_ip}`}
                </p>
                <p className="text-xs text-gray-600 font-mono">
                  {alert.created_at ? new Date(alert.created_at).toLocaleString("fr-FR") : "—"}
                </p>
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                <StatusBadge type="severity" value={alert.severity} />
                <StatusBadge type="status"   value={alert.status}   />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CrisisRoom;