import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import { useAlerts } from "../../hooks/useAlerts";
import AlertTable from "../../components/alerts/AlertTable";
import type { AlertSeverity, AlertStatus } from "../../types/alert";
import { useAuth } from "../../hooks/useAuth";
import { Role } from "../../config/roles";
import { Card, CardContent } from "../../components/ui/card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { cn } from "../../lib/utils";
import {
  Search, RefreshCw, Filter, X,
  AlertOctagon, AlertTriangle, AlertCircle, Info, MinusCircle,
} from "lucide-react";

const SEVERITIES: AlertSeverity[] = ["critical", "high", "medium", "low", "info"];
const STATUSES: AlertStatus[] = ["ouverte", "en_cours", "resolue", "classee"];

const SEVERITY_META: Record<AlertSeverity, { label: string; icon: any; color: string }> = {
  critical: { label: "Critique", icon: AlertOctagon, color: "text-red-600 dark:text-red-400" },
  high: { label: "Haute", icon: AlertTriangle, color: "text-orange-600 dark:text-orange-400" },
  medium: { label: "Moyenne", icon: AlertCircle, color: "text-amber-600 dark:text-amber-400" },
  low: { label: "Basse", icon: MinusCircle, color: "text-blue-600 dark:text-blue-400" },
  info: { label: "Info", icon: Info, color: "text-muted-foreground" },
};

const STATUS_LABEL: Record<AlertStatus, string> = {
  ouverte: "Ouverte",
  en_cours: "En cours",
  resolue: "Résolue",
  classee: "Classée",
};

const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const staggerContainer = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };

const Alerts = () => {
  const { alerts, loading, error, total, page, setPage, filter, setFilter, refresh } = useAlerts();
  const { hasAnyRole } = useAuth();
  const isReadOnly = !hasAnyRole([Role.ANALYSTE, Role.ADMINISTRATEUR]);
  const pageSize = 20;
  const totalPages = Math.ceil(total / pageSize);

  const [dateError, setDateError] = useState("");
  const [draftFilter, setDraftFilter] = useState<Record<string, string>>({});
  const [search, setSearch] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [filterOpen, setFilterOpen] = useState(false);
  const [filterPos, setFilterPos] = useState({ top: 0, right: 0 });
  const filterBtnRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const handleDraftChange = (key: string, value: string) => {
    const updated = { ...draftFilter, [key]: value || "" };
    setDraftFilter(updated);
    if (key === "from" || key === "to") {
      const fromVal = key === "from" ? value : draftFilter.from;
      const toVal = key === "to" ? value : draftFilter.to;
      setDateError(fromVal && toVal && fromVal > toVal ? "La date de début ne peut pas être postérieure à la date de fin." : "");
    }
  };

  const applyFilters = () => {
    setDateError("");
    const f: any = {};
    if (draftFilter.severity) f.severity = draftFilter.severity;
    if (draftFilter.status) f.status = draftFilter.status;
    if (search) f.search = search;
    if (draftFilter.from) f.from = draftFilter.from;
    if (draftFilter.to) {
      if (draftFilter.from && draftFilter.from > draftFilter.to) {
        setDateError("La date de début ne peut pas être postérieure à la date de fin.");
        return;
      }
      f.to = draftFilter.to;
    }
    setFilter(f as any);
    setPage(1);
  };

  const applyAndClose = () => {
    applyFilters();
    if (!dateError) setFilterOpen(false);
  };

  const resetAll = () => {
    setDraftFilter({});
    setSearch("");
    setFilter({});
    setPage(1);
    setFilterOpen(false);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await refresh();
    setRefreshing(false);
  };

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
      if (filterBtnRef.current && !filterBtnRef.current.contains(target) && menuRef.current && !menuRef.current.contains(target)) {
        setFilterOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const activeFilterCount = [draftFilter.severity, draftFilter.status, draftFilter.from, draftFilter.to].filter(Boolean).length;

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="flex flex-col gap-5">
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-foreground">Alertes</h1>
          <AnimatePresence mode="wait">
            <motion.p
              key={total}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
              className="text-sm text-muted-foreground"
            >
              {total} alerte{total > 1 ? "s" : ""} au total
            </motion.p>
          </AnimatePresence>
        </div>
        <Button variant="outline" onClick={handleRefresh}>
          <motion.span animate={refreshing ? { rotate: 360 } : { rotate: 0 }} transition={refreshing ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }} className="mr-2 inline-flex">
            <RefreshCw className="h-4 w-4" />
          </motion.span>
          Actualiser
        </Button>
      </motion.div>

      <motion.div variants={fadeUp} transition={{ duration: 0.35, ease: "easeOut" }}>
        <Card className="border-none shadow-sm">
          <CardContent className="pt-6">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex min-w-0 flex-1 items-center rounded-full border border-border bg-background px-3 py-2 shadow-sm">
                <Search className="mr-2 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Rechercher une alerte..." value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") applyFilters(); }} className="h-8 border-0 p-0 shadow-none focus-visible:ring-0" />
              </div>

              <div ref={filterBtnRef} className="relative">
                <Button variant="outline" onClick={toggleFilter} className="rounded-full">
                  <Filter className="mr-2 h-4 w-4" />
                  Filtrer
                  {activeFilterCount > 0 && (
                    <span className="ml-2 flex size-5 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-primary-foreground">
                      {activeFilterCount}
                    </span>
                  )}
                </Button>

                {createPortal(
                  <AnimatePresence>
                    {filterOpen && (
                      <motion.div ref={menuRef} initial={{ opacity: 0, y: -6, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -6, scale: 0.97 }} transition={{ duration: 0.15, ease: "easeOut" }} style={{ position: "fixed", top: filterPos.top, right: filterPos.right }} className="z-50 w-80 rounded-xl border border-border bg-popover p-4 text-popover-foreground shadow-lg">
                        <div className="mb-3 flex items-center justify-between">
                          <p className="text-sm font-medium text-foreground">Filtrer les alertes</p>
                          <button type="button" onClick={() => setFilterOpen(false)} className="text-muted-foreground">
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                        <div className="flex flex-col gap-3">
                          <div>
                            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Sévérité</p>
                            <div className="flex flex-wrap gap-1.5">
                              <FilterPill active={!draftFilter.severity} label="Toutes" onClick={() => handleDraftChange("severity", "")} />
                              {SEVERITIES.map((s) => {
                                const meta = SEVERITY_META[s];
                                return <FilterPill key={s} active={draftFilter.severity === s} label={meta.label} icon={meta.icon} iconColor={meta.color} onClick={() => handleDraftChange("severity", s)} />;
                              })}
                            </div>
                          </div>
                          <div>
                            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Statut</p>
                            <div className="flex flex-wrap gap-1.5">
                              <FilterPill active={!draftFilter.status} label="Tous" onClick={() => handleDraftChange("status", "")} />
                              {STATUSES.map((s) => <FilterPill key={s} active={draftFilter.status === s} label={STATUS_LABEL[s]} onClick={() => handleDraftChange("status", s)} />)}
                            </div>
                          </div>
                          <div>
                            <p className="mb-1.5 text-xs font-medium text-muted-foreground">Période</p>
                            <div className="grid grid-cols-2 gap-2">
                              <Input type="datetime-local" value={draftFilter.from ?? ""} max={draftFilter.to || undefined} onChange={(e) => handleDraftChange("from", e.target.value)} className="h-8 text-xs" />
                              <Input type="datetime-local" value={draftFilter.to ?? ""} min={draftFilter.from || undefined} onChange={(e) => handleDraftChange("to", e.target.value)} className="h-8 text-xs" />
                            </div>
                            <AnimatePresence>
                              {dateError && <motion.p initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.15 }} className="mt-1.5 text-xs text-destructive">{dateError}</motion.p>}
                            </AnimatePresence>
                          </div>
                        </div>
                        <div className="mt-4 flex items-center gap-2">
                          <Button size="sm" onClick={applyAndClose} className="flex-1 rounded-full">Appliquer</Button>
                          <Button size="sm" variant="ghost" onClick={resetAll} className="rounded-full">Réinitialiser</Button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>,
                  document.body
                )}
              </div>

              <Button onClick={applyFilters} className="rounded-full">Rechercher</Button>
            </div>
            {isReadOnly && <p className="mt-3 text-xs text-muted-foreground">Mode lecture seule</p>}
          </CardContent>
        </Card>
      </motion.div>

      <AnimatePresence>
        {error && <motion.p initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.2 }} className="text-sm text-destructive">{error}</motion.p>}
      </AnimatePresence>

      <motion.div variants={fadeUp} transition={{ duration: 0.35, ease: "easeOut" }}>
        <Card>
          <AnimatePresence mode="wait">
            <motion.div key={loading ? "loading" : `page-${page}-${alerts.length}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
              <AlertTable alerts={alerts} loading={loading} />
            </motion.div>
          </AnimatePresence>
        </Card>
      </motion.div>

      {total > pageSize && (
        <motion.div variants={fadeUp} transition={{ duration: 0.35, ease: "easeOut" }} className="flex items-center justify-center gap-3">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>← Précédent</Button>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span>Page</span>
            <input type="number" min={1} max={totalPages} value={page} onChange={(e) => { const p = parseInt(e.target.value); if (p >= 1 && p <= totalPages) setPage(p); }} className="h-7 w-12 rounded-md border border-input bg-background text-center text-xs text-foreground [&::-webkit-inner-spin-button]:appearance-none" />
            <span>/ {totalPages}</span>
          </div>
          <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>Suivant →</Button>
        </motion.div>
      )}
    </motion.div>
  );
};

function FilterPill({
  active, label, icon: Icon, iconColor, onClick,
}: { active: boolean; label: string; icon?: any; iconColor?: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors",
        active ? "border-primary bg-primary/10 text-foreground" : "border-border bg-background text-muted-foreground hover:bg-muted hover:text-foreground"
      )}
    >
      {Icon && <Icon className={cn("h-3 w-3", active && iconColor)} />}
      {label}
    </button>
  );
}

export default Alerts;
