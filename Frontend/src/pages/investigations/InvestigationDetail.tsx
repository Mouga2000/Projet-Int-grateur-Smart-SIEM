// src/pages/investigations/InvestigationDetail.tsx
import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import investigationService from "@/services/investigationService";
import type {
  Investigation, InvestigationStatus, InvestigationSeverity,
} from "@/types/investigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import {
  ArrowLeft, Loader2, Save,
} from "lucide-react";

// ─── Helpers ─────────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<InvestigationStatus, string> = {
  ouverte:  "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  en_cours: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  resolue:  "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  classee:  "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
};

const SEV_STYLES: Record<InvestigationSeverity, string> = {
  critical: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  high:     "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
  medium:   "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  low:      "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
};

const VERDICT_STYLES: Record<string, string> = {
  suspect:       "bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400",
  benign:        "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  confirmed:     "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  false_positive: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
};

const STATUSES: InvestigationStatus[] = ["ouverte", "en_cours", "resolue", "classee"];

// ─── Composant ───────────────────────────────────────────────────────────────

const InvestigationDetail = () => {
  const { id }   = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [inv, setInv]            = useState<Investigation | null>(null);
  const [loading, setLoading]    = useState(true);
  const [saving, setSaving]      = useState(false);
  const [editing, setEditing]    = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editDesc, setEditDesc]  = useState("");
  const [editSev, setEditSev]    = useState<InvestigationSeverity>("medium");
  const [editTags, setEditTags]  = useState("");

  // Dialog de clôture
  const [closeOpen, setCloseOpen] = useState(false);
  const [resolutionNotes, setResolutionNotes] = useState("");
  const [closeStatus, setCloseStatus] = useState<InvestigationStatus>("resolue");

  const fetchInv = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await investigationService.getById(parseInt(id));
      setInv(data);
      setEditTitle(data.title);
      setEditDesc(data.description ?? "");
      setEditSev(data.severity);
      setEditTags((data.tags ?? []).join(", "));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInv(); }, [id]);

  // ── Actions ──

  const handleSave = async () => {
    if (!inv) return;
    setSaving(true);
    try {
      const updated = await investigationService.update(inv.id, {
        title: editTitle,
        description: editDesc || undefined,
        severity: editSev,
        tags: editTags ? editTags.split(",").map((t) => t.trim()).filter(Boolean) : [],
      });
      setInv(updated);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (status: string) => {
    if (!inv) return;
    if (status === "resolue" || status === "classee") {
      setCloseStatus(status as InvestigationStatus);
      setCloseOpen(true);
      return;
    }
    setSaving(true);
    try {
      await investigationService.updateStatus(inv.id, status as InvestigationStatus);
      setInv({ ...inv, status: status as InvestigationStatus });
    } finally {
      setSaving(false);
    }
  };

  const handleClose = async () => {
    if (!inv) return;
    setSaving(true);
    try {
      await investigationService.updateStatus(inv.id, closeStatus, resolutionNotes || undefined);
      setInv({ ...inv, status: closeStatus, resolution_notes: resolutionNotes || undefined });
      setCloseOpen(false);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
      </div>
    );
  }
  if (!inv) return <p className="text-destructive text-sm py-16 text-center">Investigation introuvable.</p>;

  return (
    <div className="flex flex-col gap-6 max-w-4xl">
      {/* Header */}
      <Button variant="ghost" size="sm" className="self-start" onClick={() => navigate("/investigations")}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour aux investigations
      </Button>

      {/* Infos principales */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              {editing ? (
                <div className="flex flex-col gap-3">
                  <Input value={editTitle} onChange={(e) => setEditTitle(e.target.value)} />
                  <Textarea value={editDesc} onChange={(e) => setEditDesc(e.target.value)} rows={3} />
                  <div className="flex gap-3">
                    <div className="space-y-1">
                      <Label>Sévérité</Label>
                      <Select value={editSev} onValueChange={(v) => setEditSev(v as InvestigationSeverity)}>
                        <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="critical">Critical</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-1 flex-1">
                      <Label>Tags (séparés par des virgules)</Label>
                      <Input value={editTags} onChange={(e) => setEditTags(e.target.value)} />
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <h1 className="text-lg font-semibold">{inv.title}</h1>
                  {inv.description && <p className="text-sm text-muted-foreground mt-1">{inv.description}</p>}
                  <div className="flex items-center gap-2 mt-2 flex-wrap">
                    <Badge className={STATUS_STYLES[inv.status]} variant="outline">{inv.status}</Badge>
                    <Badge className={SEV_STYLES[inv.severity]} variant="outline">{inv.severity}</Badge>
                    {inv.mitre_tactic && <Badge variant="outline">⚔ {inv.mitre_tactic}</Badge>}
                    {inv.mitre_technique && <Badge variant="outline">🔧 {inv.mitre_technique}</Badge>}
                    {inv.tags?.map((t) => <Badge key={t} variant="secondary">{t}</Badge>)}
                  </div>
                </>
              )}
            </div>

            <div className="flex flex-col gap-2 shrink-0">
              {editing ? (
                <div className="flex gap-1">
                  <Button size="sm" onClick={handleSave} disabled={saving}>
                    <Save className="h-4 w-4 mr-1" /> Sauvegarder
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>Annuler</Button>
                </div>
              ) : (
                <Button size="sm" variant="outline" onClick={() => setEditing(true)}>
                  Modifier
                </Button>
              )}

              <Select value={inv.status} onValueChange={handleStatusChange} disabled={saving}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {STATUSES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>

          {inv.resolution_notes && (
            <div className="mt-4 p-3 bg-muted rounded-md text-sm">
              <p className="text-xs font-medium text-muted-foreground mb-1">Note de résolution :</p>
              <p>{inv.resolution_notes}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Logs associés */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Logs associés ({inv.logs?.length ?? 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {(!inv.logs || inv.logs.length === 0) && (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Aucun log associé. Depuis la page Logs, clique sur un log puis "Ajouter à une investigation".
            </p>
          )}
          <div className="flex flex-col gap-3">
            {inv.logs?.map((link) => (
              <div key={link.id} className="border rounded-lg p-3 text-sm space-y-2 hover:border-primary/30 transition-colors">
                {/* Infos ES si présentes */}
                {link.log ? (
                  <>
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center gap-2 text-xs">
                        <span className="font-mono text-muted-foreground">{new Date(link.log.timestamp).toLocaleString("fr-FR")}</span>
                        <Badge className={`text-[10px] px-1 py-0 ${
                          link.log.severity === "critical" ? "bg-red-100 text-red-800" :
                          link.log.severity === "error" ? "bg-orange-100 text-orange-800" :
                          link.log.severity === "warning" ? "bg-yellow-100 text-yellow-800" :
                          "bg-blue-100 text-blue-800"
                        }`} variant="outline">{link.log.severity}</Badge>
                      </div>
                      <span className="text-[10px] font-mono text-muted-foreground">{link.log.source_ip}</span>
                    </div>
                    <p className="text-xs font-mono text-foreground/80 truncate">{link.log.raw_message}</p>
                    <div className="flex items-center gap-1 text-[10px] text-muted-foreground">
                      <span>🖥 {link.log.host}</span>
                    </div>
                  </>
                ) : (
                  <p className="text-xs font-mono text-muted-foreground">Log #{link.log_id}</p>
                )}

                {/* Verdict + Note */}
                <div className="flex items-start gap-3 pt-1 border-t">
                  {link.verdict && (
                    <Badge className={`text-[10px] ${VERDICT_STYLES[link.verdict] ?? ""}`} variant="outline">
                      {link.verdict}
                    </Badge>
                  )}
                  {link.note && (
                    <p className="text-xs text-muted-foreground italic">"{link.note}"</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Dialog de clôture */}
      <Dialog open={closeOpen} onOpenChange={setCloseOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clôturer l'investigation</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4">
            <div className="space-y-1.5">
              <Label>Statut</Label>
              <Select value={closeStatus} onValueChange={(v) => setCloseStatus(v as InvestigationStatus)}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="resolue">Résolue</SelectItem>
                  <SelectItem value="classee">Classée (fausse alerte)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Notes de résolution</Label>
              <Textarea
                value={resolutionNotes}
                onChange={(e) => setResolutionNotes(e.target.value)}
                rows={3}
                placeholder="Analyse finale, conclusions, actions menées…"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setCloseOpen(false)}>Annuler</Button>
            <Button onClick={handleClose} disabled={saving}>
              {saving ? "Enregistrement..." : "Confirmer la clôture"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default InvestigationDetail;
