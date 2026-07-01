// src/pages/investigations/Investigations.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import investigationService from "@/services/investigationService";
import type { Investigation, InvestigationStatus } from "@/types/investigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Plus, Loader2 } from "lucide-react";

const STATUS_VARIANTS: Record<InvestigationStatus, "default" | "secondary" | "destructive" | "outline"> = {
  ouverte:  "default",
  en_cours: "secondary",
  resolue:  "outline",
  classee:  "outline",
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "text-red-500",
  high:     "text-orange-500",
  medium:   "text-yellow-500",
  low:      "text-blue-500",
};

const Investigations = () => {
  const navigate = useNavigate();
  const [items, setItems]     = useState<Investigation[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus]   = useState<string>("all");

  const [dialogOpen, setDialogOpen] = useState(false);
  const [title, setTitle]           = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity]     = useState("medium");
  const [saving, setSaving]         = useState(false);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const data = await investigationService.list({
        status: status !== "all" ? (status as InvestigationStatus) : undefined,
        size: 100,
      });
      setItems(data.items);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchItems(); }, [status]);

  const handleCreate = async () => {
    setSaving(true);
    try {
      const inv = await investigationService.create({
        title, description, severity: severity as any, tags: [], log_ids: [],
      });
      setDialogOpen(false);
      setTitle(""); setDescription("");
      navigate(`/investigations/${inv.id}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Investigations</h1>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle investigation
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Créer une investigation</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-4">
              <div className="space-y-1.5">
                <Label>Titre</Label>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Activité suspecte sur..." />
              </div>
              <div className="space-y-1.5">
                <Label>Description</Label>
                <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} />
              </div>
              <div className="space-y-1.5">
                <Label>Sévérité</Label>
                <Select value={severity} onValueChange={setSeverity}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="medium">Medium</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="critical">Critical</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button disabled={!title || saving} onClick={handleCreate}>
                {saving ? "Création..." : "Créer"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Select value={status} onValueChange={setStatus}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="Statut" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">Tous les statuts</SelectItem>
          <SelectItem value="ouverte">Ouverte</SelectItem>
          <SelectItem value="en_cours">En cours</SelectItem>
          <SelectItem value="resolue">Résolue</SelectItem>
          <SelectItem value="classee">Classée</SelectItem>
        </SelectContent>
      </Select>

      {loading && (
        <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
          <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
        </div>
      )}

      {!loading && items.length === 0 && (
        <p className="text-sm text-muted-foreground py-8 text-center">Aucune investigation.</p>
      )}

      <div className="flex flex-col gap-2">
        {items.map((inv) => (
          <Card key={inv.id} className="cursor-pointer hover:border-primary/40" onClick={() => navigate(`/investigations/${inv.id}`)}>
            <CardContent className="pt-6 flex items-start justify-between gap-4">
              <div className="flex flex-col gap-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium truncate">{inv.title}</p>
                  <Badge variant={STATUS_VARIANTS[inv.status]}>{inv.status}</Badge>
                  <span className={`text-xs font-medium ${SEVERITY_COLORS[inv.severity]}`}>
                    {inv.severity}
                  </span>
                </div>
                {inv.description && (
                  <p className="text-xs text-muted-foreground truncate">{inv.description}</p>
                )}
              </div>
              <span className="text-xs text-muted-foreground shrink-0">
                {new Date(inv.created_at).toLocaleDateString("fr-FR")}
              </span>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Investigations;