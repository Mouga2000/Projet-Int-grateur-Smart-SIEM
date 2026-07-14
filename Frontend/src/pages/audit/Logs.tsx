// src/pages/audit/Logs.tsx
import { useEffect, useRef, useState, useCallback } from "react";
import { createPortal } from "react-dom";
import { motion, AnimatePresence } from "framer-motion";
import auditService from "../../services/auditService";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../components/ui/Table";
import { cn } from "../../lib/utils";
import {
  Download, Filter, Search, X, Loader2, ScrollText, ChevronLeft, ChevronRight, FileText,
} from "lucide-react";

interface AuditLog {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource?: string;
  resourceId?: string;
  resource_type?: string;
  resource_id?: string;
  details?: unknown;
  ip_address?: string;
  ip?: string;
  timestamp: string;
}

function actionColor(action: string): string {
  const map: Record<string, string> = {
    login:          "severity-info",
    logout:         "severity-debug",
    create_rule:    "severity-error",
    update_rule:    "severity-warning",
    delete_rule:    "severity-critical",
    create_playbook: "severity-error",
    update_playbook: "severity-warning",
    delete_playbook: "severity-critical",
    execute_playbook: "badge-purple",
    purge_audit:    "severity-critical",
    create_investigation: "badge-indigo",
    investigation_ouverte: "severity-info",
    investigation_en_cours: "severity-warning",
    investigation_resolue: "severity-error",
    investigation_classee: "severity-debug",
    create_archive: "badge-cyan",
    create_user:    "severity-error",
    update_role:    "severity-warning",
  };
  return map[action] ?? "severity-debug";
}

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const rowItem = {
  hidden: { opacity: 0, y: 6 },
  show: { opacity: 1, y: 0 },
};

const Logs = () => {
  const [logs, setLogs]       = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal]     = useState(0);
  const [page, setPage]       = useState(1);
  const [from, setFrom]       = useState("");
  const [to, setTo]           = useState("");
  const [searchUser, setSearchUser] = useState("");
  const [exporting, setExporting] = useState(false);
  const [pdfExporting, setPdfExporting] = useState(false);
  const [dateError, setDateError] = useState("");
  const pageSize = 25;

  const [filterOpen, setFilterOpen] = useState(false);
  const [filterPos, setFilterPos] = useState({ top: 0, right: 0 });
  const filterBtnRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const validateDates = (): boolean => {
    if (from && to && from > to) {
      setDateError("La date de début ne peut pas être postérieure à la date de fin.");
      return false;
    }
    setDateError("");
    return true;
  };

  const fetchLogs = useCallback(async () => {
    if (!validateDates()) return;
    setLoading(true);
    try {
      const data = await auditService.getLogs({
        from: from || undefined,
        to: to || undefined,
        username: searchUser || undefined,
        page,
        size: pageSize,
      });
      setLogs(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  }, [page, from, to, searchUser]);

  useEffect(() => { fetchLogs(); // eslint-disable-line react-hooks/set-state-in-effect
  }, [fetchLogs]);

  const handleExport = async () => {
    if (!validateDates()) return;
    setExporting(true);
    try {
      const blob = await auditService.export({ from: from || undefined, to: to || undefined });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `audit-logs-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  };

  const generatePdf = async () => {
    if (!validateDates()) return;
    setPdfExporting(true);
    try {
      // Récupérer tous les logs (jusqu'à 5000) pour le rapport
      const data = await auditService.getLogs({
        from: from || undefined,
        to: to || undefined,
        username: searchUser || undefined,
        page: 1,
        size: 5000,
      });

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const rows = (data.items as any[])
        .map(
          (log) => `
        <tr>
          <td style="padding:6px 10px;border-bottom:1px solid #e5e7eb;font-family:monospace;font-size:12px;color:#6b7280">${new Date(log.timestamp).toLocaleString("fr-FR")}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #e5e7eb;font-size:12px">${log.username}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #e5e7eb;font-size:12px"><span style="background:#f3f4f6;padding:2px 8px;border-radius:4px">${log.action}</span></td>
          <td style="padding:6px 10px;border-bottom:1px solid #e5e7eb;font-size:12px;color:#6b7280">${log.resource || log.resource_type || "—"}</td>
          <td style="padding:6px 10px;border-bottom:1px solid #e5e7eb;font-family:monospace;font-size:12px;color:#6b7280">${log.ip_address || log.ip || "—"}</td>
        </tr>`
        )
        .join("");

      const html = `<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"><title>Rapport d'audit - Smart SIEM</title>
<style>
  @page { margin: 20mm 15mm; }
  body { font-family: 'Inter', Arial, sans-serif; color: #111827; margin: 0; padding: 20px; }
  h1 { font-size: 22px; font-weight: 600; margin: 0 0 4px 0; }
  .sub { font-size: 13px; color: #6b7280; margin-bottom: 24px; }
  table { width: 100%; border-collapse: collapse; }
  th { background: #f9fafb; text-align: left; padding: 8px 10px; font-size: 11px; font-weight: 600; color: #374151; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 2px solid #e5e7eb; }
  .footer { margin-top: 24px; font-size: 11px; color: #9ca3af; text-align: center; border-top: 1px solid #e5e7eb; padding-top: 16px; }
  .badge { display: inline-block; background: #f3f4f6; padding: 2px 8px; border-radius: 4px; font-size: 11px; }
</style></head>
<body>
  <h1>📋 Rapport d'audit — Smart SIEM</h1>
  <div class="sub">${data.total} entrée${data.total > 1 ? "s" : ""} • Généré le ${new Date().toLocaleString("fr-FR")}${from ? " • Du " + new Date(from).toLocaleString("fr-FR") : ""}${to ? " au " + new Date(to).toLocaleString("fr-FR") : ""}${searchUser ? " • Utilisateur : " + searchUser : ""}</div>
  <table>
    <thead><tr><th>Date</th><th>Utilisateur</th><th>Action</th><th>Ressource</th><th>IP</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
  <div class="footer">Smart SIEM — UCAC-ICAM • Document généré automatiquement</div>
  <script>window.print()</script>
</body></html>`;

      const win = window.open("", "_blank");
      if (win) {
        win.document.write(html);
        win.document.close();
      }
    } finally {
      setPdfExporting(false);
    }
  };

  const applyFilters = () => {
    setPage(1);
    fetchLogs();
    setFilterOpen(false);
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

  const activeFilterCount = [searchUser, from, to].filter(Boolean).length;
  const totalPages = Math.ceil(total / pageSize);

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
          <h1 className="text-lg font-medium">Logs d'audit</h1>
          <AnimatePresence mode="wait">
            <motion.p
              key={total}
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.2 }}
              className="text-sm text-muted-foreground"
            >
              {total.toLocaleString("fr-FR")} entrée{total > 1 ? "s" : ""}
            </motion.p>
          </AnimatePresence>
        </div>

        <div className="flex items-center gap-2">
          <div ref={filterBtnRef} className="relative">
            <Button variant="secondary" size="sm" onClick={toggleFilter}>
              <Filter className="h-4 w-4 mr-1.5" />
              Filtrer
              {activeFilterCount > 0 && (
                <span className="ml-1.5 flex size-4 items-center justify-center rounded-full bg-primary text-[0.6rem] font-medium text-primary-foreground">
                  {activeFilterCount}
                </span>
              )}
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
                    className="z-50 w-80 rounded-xl border bg-popover p-4 text-popover-foreground shadow-xl"
                  >
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-medium">Filtrer les logs d'audit</p>
                      <button type="button" onClick={() => setFilterOpen(false)} className="text-muted-foreground hover:text-foreground">
                        <X className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="flex flex-col gap-3">
                      <div>
                        <p className="mb-1.5 text-xs font-medium text-muted-foreground">Utilisateur</p>
                        <div className="flex items-center gap-2 rounded-lg border border-input bg-background px-2.5 py-1.5">
                          <Search className="h-3.5 w-3.5 text-muted-foreground" />
                          <input
                            type="text"
                            value={searchUser}
                            onChange={(e) => setSearchUser(e.target.value)}
                            placeholder="Nom d'utilisateur..."
                            className="w-full bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
                          />
                        </div>
                      </div>

                      <div>
                        <p className="mb-1.5 text-xs font-medium text-muted-foreground">Période</p>
                        <div className="grid grid-cols-2 gap-2">
                          <Input
                            type="datetime-local"
                            value={from}
                            onChange={(e) => { setFrom(e.target.value); setDateError(""); }}
                            max={to || undefined}
                            className="h-8 text-xs"
                          />
                          <Input
                            type="datetime-local"
                            value={to}
                            onChange={(e) => { setTo(e.target.value); setDateError(""); }}
                            min={from || undefined}
                            className="h-8 text-xs"
                          />
                        </div>
                        <AnimatePresence>
                          {dateError && (
                            <motion.p
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.15 }}
                              className="mt-1.5 text-xs text-destructive"
                            >
                              {dateError}
                            </motion.p>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center gap-2">
                      <Button size="sm" onClick={applyFilters} className="flex-1">
                        Appliquer
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => { setSearchUser(""); setFrom(""); setTo(""); setDateError(""); setPage(1); fetchLogs(); setFilterOpen(false); }}
                      >
                        Réinitialiser
                      </Button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>,
              document.body
            )}
          </div>

          <Button variant="secondary" size="sm" disabled={exporting} onClick={handleExport}>
            <motion.span
              animate={exporting ? { rotate: 360 } : { rotate: 0 }}
              transition={exporting ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
              className="mr-1.5 inline-flex"
            >
              {exporting ? <Loader2 className="h-4 w-4" /> : <Download className="h-4 w-4" />}
            </motion.span>
            Exporter CSV
          </Button>

          <Button variant="secondary" size="sm" disabled={pdfExporting} onClick={generatePdf}>
            <motion.span
              animate={pdfExporting ? { rotate: 360 } : { rotate: 0 }}
              transition={pdfExporting ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
              className="mr-1.5 inline-flex"
            >
              {pdfExporting ? <Loader2 className="h-4 w-4" /> : <FileText className="h-4 w-4" />}
            </motion.span>
            Rapport PDF
          </Button>
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
            className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground"
          >
            <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty */}
      <AnimatePresence>
        {!loading && logs.length === 0 && (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col items-center gap-2 py-12 text-center"
          >
            <ScrollText className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">Aucune entrée d'audit.</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      {!loading && logs.length > 0 && (
        <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="overflow-hidden rounded-xl border bg-card text-card-foreground">
          <Table className="text-xs">
            <TableHeader>
              <TableRow className="bg-muted/40">
                <TableHead>Date</TableHead>
                <TableHead>Utilisateur</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Ressource</TableHead>
                <TableHead>IP</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <AnimatePresence mode="wait">
                {logs.map((log) => (
                  <motion.tr
                    key={log.id}
                    variants={rowItem}
                    initial="hidden"
                    animate="show"
                    className="border-b last:border-0"
                  >
                    <TableCell className="font-mono text-muted-foreground">
                      {new Date(log.timestamp).toLocaleString("fr-FR")}
                    </TableCell>
                    <TableCell className="text-foreground">{log.username}</TableCell>
                    <TableCell>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${actionColor(log.action)}`}>
                        {log.action}
                      </span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {log.resource || log.resource_type || "—"}
                      {(log.resourceId || log.resource_id) && (
                        <span className="font-mono text-muted-foreground/70">#{ (log.resourceId || log.resource_id || "").slice(0, 8)}</span>
                      )}
                      {(log.details as Record<string, string>)?.method && (
                        <span className="ml-1 text-[10px] text-muted-foreground/80">({(log.details as Record<string, string>).method})</span>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-muted-foreground">{log.ip_address || log.ip || "—"}</TableCell>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </TableBody>
          </Table>
        </motion.div>
      )}

      {/* Pagination */}
      {total > pageSize && (
        <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Page {page} / {totalPages}</span>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className={cn(
                "flex size-8 items-center justify-center rounded-lg border bg-background text-foreground hover:bg-muted",
                page === 1 && "opacity-40"
              )}
            >
              <ChevronLeft className="size-4" />
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className={cn(
                "flex size-8 items-center justify-center rounded-lg border bg-background text-foreground hover:bg-muted",
                page >= totalPages && "opacity-40"
              )}
            >
              <ChevronRight className="size-4" />
            </button>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default Logs;
