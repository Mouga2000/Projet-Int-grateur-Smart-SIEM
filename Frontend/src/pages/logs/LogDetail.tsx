// src/pages/logs/LogDetail.tsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { LogEntry } from "@/types/log";
import logService from "@/services/logService";
import investigationService from "@/services/investigationService";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import SeverityBadge from "@/components/logs/SeverityBadge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowLeft, Trash2, FilePlus2, Loader2 } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Role } from "@/config/roles";

const LogDetail = () => {
  const { id }   = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { hasAnyRole } = useAuth();
  const canInvestigate = hasAnyRole([Role.ANALYSTE, Role.ADMINISTRATEUR]);

  const [log, setLog]         = useState<LogEntry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  const [investigations, setInvestigations] = useState<{ id: number; title: string }[]>([]);
  const [dialogOpen, setDialogOpen]   = useState(false);
  const [selectedInv, setSelectedInv] = useState<string>("");
  const [note, setNote]               = useState("");
  const [verdict, setVerdict]         = useState("suspect");
  const [saving, setSaving]           = useState(false);

  useEffect(() => {
    if (!id) return;
    logService.getById(id)
      .then(setLog)
      .catch(() => setError("Log introuvable."))
      .finally(() => setLoading(false));
  }, [id]);

  const openInvestigationDialog = async () => {
    const data = await investigationService.list({ size: 100 });
    setInvestigations(data.items.map((i) => ({ id: i.id, title: i.title })));
    setDialogOpen(true);
  };

  const handleAttach = async () => {
    if (!log || !selectedInv) return;
    setSaving(true);
    try {
      await investigationService.addLog(parseInt(selectedInv), log.id, note, verdict);
      setDialogOpen(false);
      setNote("");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!log) return;
    await logService.delete(log.id);
    navigate("/logs");
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
      </div>
    );
  }
  if (error || !log) return <p className="text-destructive text-sm">{error ?? "Erreur"}</p>;

  const fields: [string, string | undefined][] = [
    ["ID", log.id],
    ["Source IP", log.source_ip],
    ["Hôte", log.host],
    ["Type", log.log_type],
    ["Date", new Date(log.timestamp).toLocaleString("fr-FR")],
  ];

  return (
    <div className="flex flex-col gap-6 max-w-3xl">
      <Button variant="ghost" size="sm" className="self-start" onClick={() => navigate("/logs")}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour aux logs
      </Button>

      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <SeverityBadge severity={log.severity} />
            {log.tags.map((tag) => (
              <span key={tag} className="text-xs bg-muted px-1.5 py-0.5 rounded">{tag}</span>
            ))}
          </div>
          <h1 className="text-lg font-semibold leading-snug">{log.raw_message}</h1>
        </div>

        <div className="flex gap-2 shrink-0">
          {canInvestigate && (
            <Button variant="outline" size="sm" onClick={openInvestigationDialog}>
              <FilePlus2 className="h-4 w-4 mr-2" />
              Ajouter à une investigation
            </Button>
          )}
          <Button variant="destructive" size="sm" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Supprimer
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Détails</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full text-sm">
            <tbody>
              {fields.filter(([, v]) => v).map(([label, val]) => (
                <tr key={label} className="border-b last:border-0">
                  <td className="py-2.5 text-muted-foreground w-32 text-xs">{label}</td>
                  <td className="py-2.5 font-mono text-xs break-all">{val}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ajouter à une investigation</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4">
            <Select value={selectedInv} onValueChange={setSelectedInv}>
              <SelectTrigger>
                <SelectValue placeholder="Choisir une investigation" />
              </SelectTrigger>
              <SelectContent>
                {investigations.map((inv) => (
                  <SelectItem key={inv.id} value={String(inv.id)}>{inv.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={verdict} onValueChange={setVerdict}>
              <SelectTrigger>
                <SelectValue placeholder="Verdict" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="suspect">Suspect</SelectItem>
                <SelectItem value="benign">Bénin</SelectItem>
                <SelectItem value="confirmed">Confirmé</SelectItem>
                <SelectItem value="false_positive">Faux positif</SelectItem>
              </SelectContent>
            </Select>

            <Textarea
              placeholder="Note d'analyse (optionnel)..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDialogOpen(false)}>Annuler</Button>
            <Button disabled={!selectedInv || saving} onClick={handleAttach}>
              {saving ? "Ajout..." : "Ajouter"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LogDetail;