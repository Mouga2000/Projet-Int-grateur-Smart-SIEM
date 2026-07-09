// src/pages/admin/System.tsx
import { useEffect, useState } from "react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Loader2 } from "lucide-react";

const System = () => {
  const [config, setConfig]   = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(ENDPOINTS.admin.retention)
      .then(({ data }) => setConfig(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 max-w-xl">
      <h1 className="text-lg font-semibold">Configuration système</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Rétention des données</CardTitle>
          <CardDescription>Paramètres de purge automatique.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Logs (jours)</span>
            <span className="font-medium">{config?.log_retention_days ?? 90}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Audit (jours)</span>
            <span className="font-medium">{config?.audit_retention_days ?? 365}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Prochaine purge</span>
            <span className="font-medium">{config?.next_purge ?? "—"}</span>
          </div>
        </CardContent>
      </Card>

      <p className="text-xs text-muted-foreground">
        La modification de la rétention se fait via la page <strong>Rétention</strong> dans le menu.
      </p>
    </div>
  );
};

export default System;
