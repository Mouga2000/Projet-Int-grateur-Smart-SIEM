// src/pages/investigations/InvestigationDetail.tsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import investigationService from "@/services/investigationService";
import type { Investigation, InvestigationStatus } from "@/types/investigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { ArrowLeft, Loader2 } from "lucide-react";

const STATUSES: InvestigationStatus[] = ["ouverte", "en_cours", "resolue", "classee"];

const InvestigationDetail = () => {
  const { id }   = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [inv, setInv]         = useState<Investigation | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving]   = useState(false);

  const fetchInv = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await investigationService.getById(parseInt(id));
      setInv(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInv(); }, [id]);

  const handleStatusChange = async (status: string) => {
    if (!inv) return;
    setSaving(true);
    try {
      await investigationService.updateStatus(inv.id, status as InvestigationStatus);
      setInv({ ...inv, status: status as InvestigationStatus });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
      </div>
    );
  }
  if (!inv) return <p className="text-destructive text-sm">Investigation introuvable.</p>;

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <Button variant="ghost" size="sm" className="self-start" onClick={() => navigate("/investigations")}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour
      </Button>

      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-lg font-semibold">{inv.title}</h1>
          {inv.description && <p className="text-sm text-muted-foreground mt-1">{inv.description}</p>}
          <div className="flex items-center gap-2 mt-2">
            <Badge>{inv.severity}</Badge>
            {inv.mitre_tactic && <Badge variant="outline">{inv.mitre_tactic}</Badge>}
          </div>
        </div>

        <Select value={inv.status} onValueChange={handleStatusChange} disabled={saving}>
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
          </SelectContent>
        </Select>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Logs associés ({inv.logs?.length ?? 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {(!inv.logs || inv.logs.length === 0) && (
            <p className="text-sm text-muted-foreground">
              Aucun log associé. Ajoute des logs depuis la page Logs.
            </p>
          )}
          <div className="flex flex-col gap-2">
            {inv.logs?.map((log: any) => (
              <div key={log.id} className="border rounded-md p-3 text-sm">
                <p className="font-mono text-xs text-muted-foreground">
                  {new Date(log.timestamp).toLocaleString("fr-FR")}
                </p>
                <p className="mt-1 truncate">{log.raw_message}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default InvestigationDetail;