import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence, animate } from "framer-motion";
import { useAlertContext } from "../../context/AlertContext";
import type { Alert } from "../../types/alert";
import StatusBadge from "../../components/alerts/StatusBadge";
import api from "../../services/api";
import { cn } from "../../lib/utils";
import { Radio, ShieldAlert, Flame, CheckCircle2 } from "lucide-react";

function useCountUp(target: number, duration = 0.5) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const controls = animate(value, target, {
      duration,
      ease: "easeOut",
      onUpdate: (v) => setValue(Math.round(v)),
    });
    return () => controls.stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);
  return value;
}

const staggerContainer = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };
const fadeUp = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } };

type Tone = "red" | "orange" | "slate";
const TONE_STYLES: Record<Tone, { bg: string; border: string; label: string; value: string; glow: string; chip: string }> = {
  red: { bg: "bg-red-500/5", border: "border-red-200 dark:border-red-900/60", label: "text-red-700 dark:text-red-400", value: "text-red-700 dark:text-red-300", glow: "shadow-[0_0_30px_-12px_rgba(239,68,68,0.22)]", chip: "bg-red-500/10 text-red-700 dark:text-red-400" },
  orange: { bg: "bg-orange-500/5", border: "border-orange-200 dark:border-orange-900/60", label: "text-orange-700 dark:text-orange-400", value: "text-orange-700 dark:text-orange-300", glow: "shadow-[0_0_30px_-12px_rgba(249,115,22,0.22)]", chip: "bg-orange-500/10 text-orange-700 dark:text-orange-400" },
  slate: { bg: "bg-card", border: "border-border", label: "text-muted-foreground", value: "text-foreground", glow: "", chip: "bg-muted text-muted-foreground" },
};

function CrisisStat({ label, value, tone, icon: Icon, pulse }: { label: string; value: number; tone: Tone; icon: any; pulse?: boolean }) {
  const t = TONE_STYLES[tone];
  const count = useCountUp(value);
  return (
    <motion.div variants={fadeUp} whileHover={{ y: -3 }} transition={{ duration: 0.2 }} className={cn("relative overflow-hidden rounded-xl border p-4", t.bg, t.border, t.glow)}>
      {pulse && value > 0 && <motion.span className="absolute right-3 top-3 size-2 rounded-full bg-red-500" animate={{ opacity: [1, 0.3, 1], scale: [1, 1.4, 1] }} transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }} />}
      <div className="mb-2 flex items-center gap-2">
        <div className={cn("flex size-7 items-center justify-center rounded-lg", t.chip)}><Icon className="size-3.5" /></div>
        <p className={cn("text-xs font-medium", t.label)}>{label}</p>
      </div>
      <motion.p key={count} initial={{ opacity: 0.5, y: 2 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.15 }} className={cn("text-4xl font-bold tabular-nums", t.value)}>
        {count}
      </motion.p>
    </motion.div>
  );
}

const CrisisRoom = () => {
  const navigate = useNavigate();
  const { liveAlerts } = useAlertContext();
  const [criticals, setCriticals] = useState<Alert[]>([]);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchCriticals = useCallback(async () => {
    try {
      const { data } = await api.get("/alerts", { params: { severity: "critical", size: 50 } });
      setCriticals(data.items);
      setLastRefresh(new Date());
    } catch {}
  }, []);

  useEffect(() => {
    fetchCriticals();
    const interval = setInterval(fetchCriticals, 5000);
    return () => clearInterval(interval);
  }, [fetchCriticals]);

  const allCriticals = [...liveAlerts.filter((a) => a.severity === "critical"), ...criticals].filter((a, i, arr) => arr.findIndex((x) => x.id === a.id) === i);
  const openCount = allCriticals.filter((a) => a.status === "ouverte").length;
  const progressCount = allCriticals.filter((a) => a.status === "en_cours").length;
  const resolvedCount = allCriticals.filter((a) => a.status === "resolue").length;

  return (
    <div className="flex h-full flex-col gap-4">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }} className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <motion.span className="relative flex size-2" animate={{ opacity: [1, 0.4, 1] }} transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}>
            <span className="absolute inline-flex h-full w-full rounded-full bg-red-500" />
          </motion.span>
          <h1 className="flex items-center gap-2 text-lg font-semibold tracking-wide text-foreground">
            <Radio className="size-4 text-red-600 dark:text-red-400" />
            CRISIS ROOM
          </h1>
          <span className="text-xs font-mono text-muted-foreground">— LIVE</span>
        </div>
        <motion.div key={lastRefresh.getTime()} initial={{ opacity: 0.4 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }} className="text-xs font-mono text-muted-foreground">
          Dernière maj : {lastRefresh.toLocaleTimeString("fr-FR")}
        </motion.div>
      </motion.div>

      <motion.div variants={staggerContainer} initial="hidden" animate="show" className="grid grid-cols-3 gap-4">
        <CrisisStat label="Alertes critiques actives" value={openCount} tone="red" icon={Flame} pulse />
        <CrisisStat label="En cours de traitement" value={progressCount} tone="orange" icon={ShieldAlert} />
        <CrisisStat label="Résolues" value={resolvedCount} tone="slate" icon={CheckCircle2} />
      </motion.div>

      <div className="flex-1 overflow-y-auto">
        <motion.div variants={staggerContainer} initial="hidden" animate="show" className="space-y-2">
          <AnimatePresence mode="popLayout">
            {allCriticals.length === 0 && (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="py-12 text-center text-sm text-muted-foreground">
                Aucune alerte critique active.
              </motion.div>
            )}
            {allCriticals.map((alert) => (
              <motion.div key={alert.id} layout variants={fadeUp} initial="hidden" animate="show" exit={{ opacity: 0, x: -12, transition: { duration: 0.15 } }} whileHover={{ x: 2, borderColor: "rgba(239,68,68,0.35)" }} transition={{ duration: 0.2 }} className="flex cursor-pointer items-start justify-between gap-4 rounded-lg border border-border bg-card p-4" onClick={() => navigate(`/alerts/${alert.id}`)}>
                <div className="flex min-w-0 flex-col gap-1">
                  <p className="truncate text-sm font-medium text-foreground">{alert.title}</p>
                  <p className="truncate text-xs text-muted-foreground">{alert.host || alert.source_ip || "—"}{alert.source_ip && ` · ${alert.source_ip}`}</p>
                  <p className="text-xs font-mono text-muted-foreground">{alert.created_at ? new Date(alert.created_at).toLocaleString("fr-FR") : "—"}</p>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-2">
                  <StatusBadge type="severity" value={alert.severity} />
                  <StatusBadge type="status" value={alert.status} />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
};

export default CrisisRoom;
