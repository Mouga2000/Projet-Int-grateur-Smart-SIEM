// src/pages/logs/Logs.tsx
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import logService from "@/services/logService";
import type { LogEntry, Severity } from "@/types/log";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import LogTable from "@/components/logs/LogTable";
import { cn } from "@/lib/utils";
import {
  RefreshCw, Search, Filter, Check,
  AlertOctagon, AlertTriangle, AlertCircle, Info, Bug, LayoutList,
} from "lucide-react";

const SEVERITIES: Severity[] = ["critical", "error", "warning", "info", "debug"];

const SEVERITY_META: Record<Severity, { label: string; icon: any; color: string }> = {
  critical: { label: "Critique", icon: AlertOctagon,  color: "text-red-500" },
  error:    { label: "Erreur",   icon: AlertTriangle, color: "text-orange-500" },
  warning:  { label: "Alerte",   icon: AlertCircle,   color: "text-amber-500" },
  info:     { label: "Info",     icon: Info,          color: "text-blue-500" },
  debug:    { label: "Debug",    icon: Bug,            color: "text-gray-500" },
};

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const Logs = () => {
  const [logs, setLogs]       = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal]     = useState(0);
  const [page, setPage]       = useState(1);
  const [query, setQuery]     = useState("");
  const [severity, setSeverity] = useState<string>("all");
  const [filterOpen, setFilterOpen] = useState(false);
  const [filterPos, setFilterPos] = useState({ top: 0, right: 0 });
  const filterRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const pageSize = 50;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      if (query || severity !== "all") {
        const data = await logService.search({
          query: query || "*",
          severities: severity !== "all" ? [severity] : [],
          page,
          size: pageSize,
        });
        setLogs(data.items);
        setTotal(data.total);
      } else {
        const data = await logService.list(page, pageSize);
        setLogs(data.items);
        setTotal(data.total);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page]);
  useEffect(() => { setPage(1); fetchLogs(); }, [severity]);

  // Fermer le menu de filtre au clic extérieur (bouton ET menu en portal)
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        filterRef.current && !filterRef.current.contains(target) &&
        menuRef.current && !menuRef.current.contains(target)
      ) {
        setFilterOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleFilter = () => {
    if (!filterOpen && filterRef.current) {
      const rect = filterRef.current.getBoundingClientRect();
      setFilterPos({ top: rect.bottom + 8, right: window.innerWidth - rect.right });
    }
    setFilterOpen((o) => !o);
  };

  const handleSearch = () => { setPage(1); fetchLogs(); };

  const totalPages = Math.ceil(total / pageSize);
  const activeSeverityMeta = severity !== "all" ? SEVERITY_META[severity as Severity] : null;

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-5"
    >
      {/* Titre + Actualiser */}
      <motion.div
        variants={fadeUp}
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-xl font-semibold">Logs</h1>
          <AnimatePresence mode="wait">
            <motion.p
              key={total}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
              className="text-sm text-muted-foreground"
            >
              {total.toLocaleString("fr-FR")} log{total > 1 ? "s" : ""} au total
            </motion.p>
          </AnimatePresence>
        </div>
        <Button variant="outline" size="sm" onClick={fetchLogs} className="rounded-full">
          <motion.span
            animate={loading ? { rotate: 360 } : { rotate: 0 }}
            transition={loading ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
            className="mr-2 inline-flex"
          >
            <RefreshCw className="h-4 w-4" />
          </motion.span>
          Actualiser
        </Button>
      </motion.div>

      {/* Recherche + filtre */}
      <motion.div variants={fadeUp} transition={{ duration: 0.35, ease: "easeOut" }}>
        <Card className="border-none shadow-sm">
          <CardContent>
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex min-w-0 flex-1 items-center rounded-full border bg-background px-3 py-2 shadow-sm">
                <Search className="mr-2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Rechercher dans les messages..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") handleSearch(); }}
                  className="h-8 border-0 bg-transparent p-0 shadow-none focus-visible:ring-0"
                />
              </div>

              {/* Bouton filtre + sous-menu animé (rendu en portal) */}
              <div ref={filterRef} className="relative">
                <Button
                  variant="outline"
                  onClick={toggleFilter}
                  className="rounded-full"
                >
                  {activeSeverityMeta ? (
                    <activeSeverityMeta.icon className={cn("mr-2 h-4 w-4", activeSeverityMeta.color)} />
                  ) : (
                    <Filter className="mr-2 h-4 w-4" />
                  )}
                  {activeSeverityMeta ? activeSeverityMeta.label : "Filtrer"}
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
                        className="z-50 w-48 overflow-hidden rounded-xl border bg-popover p-1.5 shadow-lg"
                      >
                        <FilterOption
                          active={severity === "all"}
                          icon={LayoutList}
                          label="Toutes les sévérités"
                          onClick={() => { setSeverity("all"); setFilterOpen(false); }}
                        />
                        <div className="my-1 h-px bg-border" />
                        {SEVERITIES.map((s) => {
                          const meta = SEVERITY_META[s];
                          return (
                            <FilterOption
                              key={s}
                              active={severity === s}
                              icon={meta.icon}
                              iconColor={meta.color}
                              label={meta.label}
                              onClick={() => { setSeverity(s); setFilterOpen(false); }}
                            />
                          );
                        })}
                      </motion.div>
                    )}
                  </AnimatePresence>,
                  document.body
                )}
              </div>

              <Button onClick={handleSearch} className="rounded-full">
                Rechercher
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Tableau des logs */}
      <motion.div variants={fadeUp} transition={{ duration: 0.35, ease: "easeOut" }}>
        <Card className="border-none shadow-sm">
          <CardContent className="pt-6">
            <AnimatePresence mode="wait">
              <motion.div
                key={loading ? "loading" : `page-${page}-${severity}-${logs.length}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <LogTable logs={logs} loading={loading} />
              </motion.div>
            </AnimatePresence>
          </CardContent>
        </Card>
      </motion.div>

      {/* Pagination */}
      {total > pageSize && (
        <motion.div
          variants={fadeUp}
          transition={{ duration: 0.35, ease: "easeOut" }}
          className="flex items-center justify-between text-sm"
        >
          <span className="text-muted-foreground">
            Page {page} / {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="rounded-full"
            >
              Précédent
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="rounded-full"
            >
              Suivant
            </Button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

// ─── Option du sous-menu de filtre ──────────────────────────────────────────

function FilterOption({
  active, icon: Icon, iconColor, label, onClick,
}: { active: boolean; icon: any; iconColor?: string; label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm",
        active ? "bg-muted font-medium text-foreground" : "text-muted-foreground"
      )}
    >
      <Icon className={cn("h-4 w-4", active && iconColor)} />
      <span className="flex-1 text-left">{label}</span>
      {active && <Check className="h-3.5 w-3.5" />}
    </button>
  );
}

export default Logs;