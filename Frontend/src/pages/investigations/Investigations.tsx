// src/pages/investigations/Investigations.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import investigationService from "@/services/investigationService";
import type { Investigation, InvestigationStatus, InvestigationSeverity } from "@/types/investigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Plus, Loader2, ChevronLeft, ChevronRight } from "lucide-react";

const STATUS_STYLES: Record<InvestigationStatus, string> = {
  ouverte:  "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  en_cours: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  resolue:  "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  classee:  "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
};

const SEV_COLORS: Record<InvestigationSeverity, string> = {
  critical: "text-red-500",
  high:     "text-orange-500",
  medium:   "text-yellow-500",
  low:      "text-blue-500",
};

const PAGE_SIZE = 20;

const Investigations = () => {
  const navigate = useNavigate();
  const [items, setItems]       = useState<Investigation[]>([]);
  const [loading, setLoading]   = useState(true);
  const [status, setStatus]     = useState<string>("all");
  const [page, setPage]         = useState(1);
  const [total, setTotal]       = useState(0);
  const [pages, setPages]       = useState(1);

  // Create dialog
  const [dialogOpen, setDialogOpen] = useState(false);
  const [title, setTitle]           = useState("");
  const [description, setDescription] = useState("");
  const [severity, setSeverity]     = useState<InvestigationSeverity>("medium");
  const [saving, setSaving]         = useState(false);

  const fetchItems = async (p: number) => {
    setLoading(true);
    try {
      const data = await investigationService.list({
        status: status !== "all" ? (status as InvestigationStatus) : undefined,
        page: p,
        size: PAGE_SIZE,
      });
      setItems(data.items);
      setTotal(data.total);
      setPages(data.pages);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setPage(1); fetchItems(1); }, [status]);
  useEffect(() => { fetchItems(page); }, [page]);

  const handleCreate = async () => {
    if (!title.trim()) return;
    setSaving(true);
    try {
      const inv = await investigationService.create({
        title: title.trim(),
        description: description.trim() || undefined,
        severity,
        tags: [],
        log_ids: [],
      });
      setDialogOpen(false);
      setTitle(""); setDescription(""); setSeverity("medium");
      navigate(`/investigations/${inv.id}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Investigations</h1>
          {!loading && <p className="text-xs text-muted-foreground mt-0.5">{total} au total</p>}
        </div>

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
                <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={3} placeholder="Contexte, éléments observés..." />
              </div>
              <div className="space-y-1.5">
                <Label>Sévérité</Label>
                <Select value={severity} onValueChange={(v) => setSeverity(v as InvestigationSeverity)}>
                  <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
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
              <Button disabled={!title.trim() || saving} onClick={handleCreate}>
                {saving ? "Création..." : "Créer"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filtres */}
      <div className="flex gap-3">
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
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
          <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
        </div>
      )}

      {/* Empty */}
      {!loading && items.length === 0 && (
        <p className="text-sm text-muted-foreground py-8 text-center">Aucune investigation.</p>
      )}

      {/* Liste */}
      <div className="flex flex-col gap-2">
        {items.map((inv) => (
          <Card
            key={inv.id}
            className="cursor-pointer hover:border-primary/40 transition-colors"
            onClick={() => navigate(`/investigations/${inv.id}`)}
          >
            <CardContent className="pt-5 pb-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex flex-col gap-1.5 min-w-0 flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <p className="text-sm font-medium truncate">{inv.title}</p>
                    <Badge className={`text-[11px] ${STATUS_STYLES[inv.status]}`} variant="outline">
                      {inv.status}
                    </Badge>
                    <span className={`text-[11px] font-medium ${SEV_COLORS[inv.severity]}`}>
                      {inv.severity}
                    </span>
                  </div>
                  {inv.description && (
                    <p className="text-xs text-muted-foreground line-clamp-1">{inv.description}</p>
                  )}
                  <div className="flex items-center gap-3 text-[11px] text-muted-foreground">
                    <span>{inv.log_ids?.length ?? 0} log(s)</span>
                    {inv.tags?.map((t) => (
                      <span key={t} className="bg-muted px-1.5 py-0.5 rounded">{t}</span>
                    ))}
                  </div>
                </div>
                <span className="text-[11px] text-muted-foreground shrink-0 pt-0.5">
                  {new Date(inv.created_at).toLocaleDateString("fr-FR")}
                </span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      {pages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            <ChevronLeft className="h-4 w-4" /> Précédent
          </Button>
          <span className="text-xs text-muted-foreground">
            Page {page} / {pages}
          </span>
          <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            Suivant <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
};

export default Investigations;
