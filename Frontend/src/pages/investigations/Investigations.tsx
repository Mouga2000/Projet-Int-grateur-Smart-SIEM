// src/pages/investigations/Investigations.tsx
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import investigationService from "@/services/investigationService";
import type { Investigation, InvestigationStatus, InvestigationSeverity } from "@/types/investigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import {
  Plus, Loader2, ChevronLeft, ChevronRight, FileSearch, X, Filter, Check,
  AlertOctagon, AlertTriangle, AlertCircle, MinusCircle, Tag, ScrollText, Search, LayoutList,
} from "lucide-react";

const STATUS_STYLES: Record<InvestigationStatus, string> = {
  ouverte:  "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  en_cours: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
  resolue:  "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  classee:  "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
};

const STATUS_LABEL: Record<InvestigationStatus, string> = {
  ouverte: "Ouverte",
  en_cours: "En cours",
  resolue: "Résolue",
  classee: "Classée",
};

const SEV_META: Record<InvestigationSeverity, { color: string; icon: any; chip: string; border: string }> = {
  critical: { color: "text-red-500",    icon: AlertOctagon,  chip: "bg-red-500/10",    border: "border-l-red-500" },
  high:     { color: "text-orange-500", icon: AlertTriangle, chip: "bg-orange-500/10", border: "border-l-orange-500" },
  medium:   { color: "text-yellow-500", icon: AlertCircle,   chip: "bg-yellow-500/10", border: "border-l-yellow-500" },
  low:      { color: "text-blue-500",   icon: MinusCircle,   chip: "bg-blue-500/10",   border: "border-l-blue-500" },
};

const PAGE_SIZE = 20;
const STATUS_FILTERS: { value: string; label: string }[] = [
  { value: "all",      label: "Tous les statuts" },
  { value: "ouverte",  label: "Ouverte" },
  { value: "en_cours", label: "En cours" },
  { value: "resolue",  label: "Résolue" },
  { value: "classee",  label: "Classée" },
];

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const cardItem = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0 },
};

// ─── Dialog animé (Radix + framer-motion) ───────────────────────────────────
// Le composant shadcn <Dialog> par défaut anime via des classes CSS Radix
// (data-state=open/closed), pas via motion. Ici on pilote nous-mêmes le
// montage avec forceMount + AnimatePresence pour une animation 100% motion.

function AnimatedDialog({
  open, onOpenChange, trigger, title, children, footer,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  trigger: React.ReactNode;
  title: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <DialogPrimitive.Trigger asChild>{trigger}</DialogPrimitive.Trigger>
      <AnimatePresence>
        {open && (
          <DialogPrimitive.Portal forceMount>
            <DialogPrimitive.Overlay asChild forceMount>
              <motion.div
                className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              />
            </DialogPrimitive.Overlay>
            <DialogPrimitive.Content asChild forceMount>
              <motion.div
                initial={{ opacity: 0, scale: 0.96, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.96, y: 8 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-background p-6 shadow-lg"
              >
                <div className="mb-4 flex items-center justify-between">
                  <DialogPrimitive.Title className="text-base font-semibold">
                    {title}
                  </DialogPrimitive.Title>
                  <DialogPrimitive.Close className="text-muted-foreground">
                    <X className="h-4 w-4" />
                  </DialogPrimitive.Close>
                </div>

                {children}

                <div className="mt-5 flex justify-end gap-2">{footer}</div>
              </motion.div>
            </DialogPrimitive.Content>
          </DialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </DialogPrimitive.Root>
  );
}

const Investigations = () => {
  const navigate = useNavigate();
  const [items, setItems]       = useState<Investigation[]>([]);
  const [loading, setLoading]   = useState(true);
  const [status, setStatus]     = useState<string>("all");
  const [search, setSearch]     = useState("");
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

  // Filtre de statut (menu en portal)
  const [filterOpen, setFilterOpen] = useState(false);
  const [filterPos, setFilterPos] = useState({ top: 0, right: 0 });
  const filterBtnRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleFilter = () => {
    if (!filterOpen && filterBtnRef.current) {
      const rect = filterBtnRef.current.getBoundingClientRect();
      setFilterPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
    }
    setFilterOpen((o) => !o);
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        filterBtnRef.current && !filterBtnRef.current.contains(target) &&
        menuRef.current && !menuRef.current.contains(target)
      ) {
        setFilterOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const activeStatusLabel = STATUS_FILTERS.find((f) => f.value === status)?.label ?? "Filtrer";

  const filteredItems = search.trim()
    ? items.filter((inv) =>
        inv.title.toLowerCase().includes(search.trim().toLowerCase()) ||
        inv.description?.toLowerCase().includes(search.trim().toLowerCase())
      )
    : items;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-5"
    >
      {/* Header */}
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Investigations</h1>
          <AnimatePresence mode="wait">
            {!loading && (
              <motion.p
                key={total}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.2 }}
                className="text-xs text-muted-foreground mt-0.5"
              >
                {total} au total
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        <AnimatedDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          title="Créer une investigation"
          trigger={
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Nouvelle investigation
            </Button>
          }
          footer={
            <>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button disabled={!title.trim() || saving} onClick={handleCreate}>
                {saving ? "Création..." : "Créer"}
              </Button>
            </>
          }
        >
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
              <div className="flex flex-wrap gap-1.5">
                {(["low", "medium", "high", "critical"] as InvestigationSeverity[]).map((s) => {
                  const meta = SEV_META[s];
                  const Icon = meta.icon;
                  return (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setSeverity(s)}
                      className={cn(
                        "relative flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium capitalize",
                        severity === s ? "border-primary bg-primary/10 text-foreground" : "border-input text-muted-foreground"
                      )}
                    >
                      <Icon className={cn("h-3.5 w-3.5", severity === s && meta.color)} />
                      {s}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </AnimatedDialog>
      </motion.div>

      {/* Recherche + filtres */}
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex flex-wrap items-center gap-3">
        <div className="flex min-w-0 flex-1 items-center rounded-full border bg-background px-3 py-2 shadow-sm">
          <Search className="mr-2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher une investigation..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="h-8 border-0 bg-transparent p-0 shadow-none focus-visible:ring-0"
          />
        </div>
        <div ref={filterBtnRef} className="relative">
          <Button variant="outline" onClick={toggleFilter} className="rounded-full">
            <Filter className="mr-2 h-4 w-4" />
            {activeStatusLabel}
          </Button>

          {createPortal(
            <AnimatePresence>
              {filterOpen && (
                <motion.div
                  ref={menuRef}
                  initial={{ opacity: 0, y: -6, scale: 0.97 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -6, scale: 0.97 }}
                  transition={{ duration: 0.15, ease: "easeOut" }}
                  style={{ position: "fixed", top: filterPos.top, right: filterPos.right }}
                  className="z-50 w-52 overflow-hidden rounded-xl border bg-popover p-1.5 shadow-lg"
                >
                  {STATUS_FILTERS.map((f) => (
                    <button
                      key={f.value}
                      type="button"
                      onClick={() => { setStatus(f.value); setFilterOpen(false); }}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm",
                        status === f.value ? "bg-muted font-medium text-foreground" : "text-muted-foreground"
                      )}
                    >
                      <LayoutList className="h-3.5 w-3.5" />
                      <span className="flex-1 text-left">{f.label}</span>
                      {status === f.value && <Check className="h-3.5 w-3.5" />}
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>,
            document.body
          )}
        </div>
      </motion.div>

      {/* Loading */}
      <AnimatePresence>
        {loading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center justify-center py-12 text-muted-foreground gap-2"
          >
            <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty */}
      <AnimatePresence>
        {!loading && filteredItems.length === 0 && (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center gap-2 py-12 text-center"
          >
            <FileSearch className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              {search ? "Aucune investigation ne correspond à la recherche." : "Aucune investigation."}
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Liste */}
      {!loading && filteredItems.length > 0 && (
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="show"
          className="flex flex-col gap-2.5"
        >
          <AnimatePresence mode="popLayout">
            {filteredItems.map((inv) => {
              const meta = SEV_META[inv.severity];
              const SevIcon = meta.icon;
              return (
                <motion.div
                  key={inv.id}
                  layout
                  variants={cardItem}
                  exit={{ opacity: 0, transition: { duration: 0.15 } }}
                >
                  <Card
                    className={cn("cursor-pointer overflow-hidden border-l-4 py-0", meta.border)}
                    onClick={() => navigate(`/investigations/${inv.id}`)}
                  >
                    <CardContent className="flex items-start gap-4 px-5 py-4">
                      <div className={cn("mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl", meta.chip)}>
                        <SevIcon className={cn("size-4", meta.color)} />
                      </div>

                      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="text-sm font-semibold truncate">{inv.title}</p>
                          <Badge className={`text-[11px] ${STATUS_STYLES[inv.status]}`} variant="outline">
                            {STATUS_LABEL[inv.status]}
                          </Badge>
                        </div>
                        {inv.description && (
                          <p className="text-xs text-muted-foreground line-clamp-1">{inv.description}</p>
                        )}
                        <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                          <span className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
                            <ScrollText className="size-3" />
                            {inv.log_ids?.length ?? 0} log(s)
                          </span>
                          {inv.tags?.map((t) => (
                            <span key={t} className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5">
                              <Tag className="size-2.5" />
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>

                      <span className="shrink-0 whitespace-nowrap pt-0.5 text-[11px] text-muted-foreground">
                        {new Date(inv.created_at).toLocaleDateString("fr-FR")}
                      </span>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Pagination */}
      {pages > 1 && (
        <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-center gap-3">
          <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
            <ChevronLeft className="h-4 w-4" /> Précédent
          </Button>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span>Page</span>
            <input
              type="number"
              min={1}
              max={pages}
              value={page}
              onChange={(e) => {
                const p = parseInt(e.target.value);
                if (p >= 1 && p <= pages) setPage(p);
              }}
              className="w-12 h-7 rounded-md border border-input bg-transparent text-center text-xs text-foreground [&::-webkit-inner-spin-button]:appearance-none"
            />
            <span>/ {pages}</span>
          </div>
          <Button variant="outline" size="sm" disabled={page >= pages} onClick={() => setPage(page + 1)}>
            Suivant <ChevronRight className="h-4 w-4" />
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
};

export default Investigations;