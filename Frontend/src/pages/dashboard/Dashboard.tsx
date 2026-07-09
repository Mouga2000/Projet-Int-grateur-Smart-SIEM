// src/pages/dashboard/Dashboard.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence, animate } from "framer-motion";
import { cn } from "../../lib/utils";
import { useAuth } from "../../hooks/useAuth";
import api from "../../services/api";
import logService from "../../services/logService";
import type { LogEntry, TimelineResponse } from "../../types/log";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "../../components/ui/tabs-dashboard";

// Cache timeline 30s entre les refreshes du Dashboard
let _timelineCache: { data: TimelineResponse; ts: number } | null = null;
import { Button } from "../../components/ui/Button";
import LogTable from "../../components/logs/LogTable";
import {
  FileSearch, AlertTriangle, Activity, Clock,
  ShieldAlert, LayoutGrid, Network, ListTree, LineChart as LineChartIcon,
} from "lucide-react";
import {
  AreaChart, Area,
  BarChart, Bar,
  PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";

// ─── Couleurs ───────────────────────────────────────────────────────────────

const SEV_COLORS: Record<string, string> = {
  critical: "#ef4444",
  error:    "#f97316",
  warning:  "#eab308",
  info:     "#3b82f6",
  debug:    "#6b7280",
};

const TYPE_COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ec4899", "#14b8a6"];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function countBy<T>(arr: T[], key: keyof T): { name: string; value: number }[] {
  const map: Record<string, number> = {};
  for (const item of arr) {
    const k = String(item[key] ?? "inconnu");
    map[k] = (map[k] || 0) + 1;
  }
  return Object.entries(map)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);
}

function formatHour(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" })
      + " " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  }
  catch { return ts; }
}

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.06 },
  },
};

const panelTransition = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" as const } },
  exit: { opacity: 0, y: -8, transition: { duration: 0.15 } },
} as const;

// ─── Count-up animé ──────────────────────────────────────────────────────────

function useCountUp(target: number, active: boolean, duration = 0.6) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!active) return;
    const controls = animate(0, target, {
      duration,
      ease: "easeOut",
      onUpdate: (v) => setValue(Math.round(v)),
    });
    return () => controls.stop();
  }, [target, active, duration]);

  return active ? value : 0;
}

// ─── Composant stat card ─────────────────────────────────────────────────────

type Tone = "indigo" | "red" | "orange" | "amber";

const TONE_STYLES: Record<Tone, { chip: string; glow: string; bar: string; ring: string }> = {
  indigo: {
    chip: "bg-indigo-500/10 text-indigo-500",
    glow: "hover:shadow-indigo-500/10",
    bar:  "from-indigo-500 to-indigo-400",
    ring: "ring-indigo-500/15",
  },
  red: {
    chip: "bg-red-500/10 text-red-500",
    glow: "hover:shadow-red-500/10",
    bar:  "from-red-500 to-red-400",
    ring: "ring-red-500/15",
  },
  orange: {
    chip: "bg-orange-500/10 text-orange-500",
    glow: "hover:shadow-orange-500/10",
    bar:  "from-orange-500 to-orange-400",
    ring: "ring-orange-500/15",
  },
  amber: {
    chip: "bg-amber-500/10 text-amber-500",
    glow: "hover:shadow-amber-500/10",
    bar:  "from-amber-500 to-amber-400",
    ring: "ring-amber-500/15",
  },
};

function StatCard({
  label, value, icon: Icon, tone, loading,
}: { label: string; value: number; icon: any; tone: Tone; loading: boolean }) {
  const t = TONE_STYLES[tone];
  const count = useCountUp(value, !loading);

  return (
    <motion.div variants={fadeUp} whileHover={{ y: -3 }} transition={{ duration: 0.2 }}>
      <Card
        className={cn(
          "relative overflow-hidden border-none shadow-sm ring-1 ring-inset transition-shadow duration-300 hover:shadow-lg",
          t.ring, t.glow
        )}
      >
      

        <CardContent className="pt-6">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="text-xs font-medium text-muted-foreground">{label}</p>
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div
                    key="skeleton"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="mt-2 h-7 w-16 animate-pulse rounded bg-muted"
                  />
                ) : (
                  <motion.p
                    key="value"
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -4 }}
                    transition={{ duration: 0.15 }}
                    className="mt-1 text-3xl font-bold tracking-tight tabular-nums"
                  >
                    {count.toLocaleString("fr-FR")}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>

            <motion.div
              className={cn("flex size-10 shrink-0 items-center justify-center rounded-xl", t.chip)}
              whileHover={{ scale: 1.08, rotate: 4 }}
              transition={{ type: "spring", stiffness: 300, damping: 15 }}
            >
              <Icon className="size-5" />
            </motion.div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// Petite carte graphique réutilisable, avec titre + apparition douce
function ChartCard({
  title, height = 220, children,
}: { title: string; height?: number; children: React.ReactNode }) {
  return (
    <motion.div variants={fadeUp}>
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={height}>
            {children as any}
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </motion.div>
  );
}

// ─── Tabs config ─────────────────────────────────────────────────────────────

const TABS = [
  { value: "overview", label: "Vue d'ensemble", icon: LayoutGrid },
  { value: "sources",  label: "Sources",         icon: Network },
  { value: "types",    label: "Types & menace",  icon: ListTree },
  { value: "trend",    label: "Tendance",        icon: LineChartIcon },
] as const;

// ─── Dashboard ───────────────────────────────────────────────────────────────

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [logs, setLogs]           = useState<LogEntry[]>([]);
  const [allLogs, setAllLogs]     = useState<LogEntry[]>([]);
  const [timeline, setTimeline]   = useState<TimelineResponse | null>(null);
  const [severityDist, setSeverityDist] = useState<Record<string, number> | null>(null);
  const [topHosts, setTopHosts]   = useState<{ name: string; value: number }[]>([]);
  const [topIPs, setTopIPs]       = useState<{ name: string; value: number }[]>([]);
  const [typeData, setTypeData]   = useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading]     = useState(true);
  const [tab, setTab]             = useState<(typeof TABS)[number]["value"]>("overview");

  useEffect(() => {
    let cancelled = false;

    const fetchAll = async () => {
      try {
        const recent = await logService.list(1, 10);
        if (cancelled) return;
        setLogs(recent.items);

        const full = await logService.list(1, 50);
        if (cancelled) return;
        setAllLogs(full.items);

        try {
          const dist = await api.get("/logs/severity-distribution");
          if (!cancelled) setSeverityDist(dist.data);
        } catch {}

        try {
          const [hosts, ips, types] = await Promise.all([
            api.get("/logs/top/host", { params: { size: 6 } }),
            api.get("/logs/top/source_ip", { params: { size: 6 } }),
            api.get("/logs/top/log_type", { params: { size: 10 } }),
          ]);
          if (!cancelled) {
            setTopHosts(hosts.data);
            setTopIPs(ips.data);
            setTypeData(types.data);
          }
        } catch {}

        if (_timelineCache && Date.now() - _timelineCache.ts < 30000) {
          setTimeline(_timelineCache.data);
        } else {
          const tl = await logService.timeline({ interval: "1h" });
          if (!cancelled) {
            _timelineCache = { data: tl, ts: Date.now() };
            setTimeline(tl);
          }
        }
      } catch {
        // Requête individuelle échouée → on continue avec les données partielles
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetchAll();
    return () => { cancelled = true; };
  }, []);

  // ── Métriques ──
  const criticalCount = severityDist?.critical ?? allLogs.filter((l) => l.severity === "critical").length;
  const errorCount    = severityDist?.error ?? allLogs.filter((l) => l.severity === "error").length;
  const warnCount     = severityDist?.warning ?? allLogs.filter((l) => l.severity === "warning").length;
  const total         = timeline?.total ?? allLogs.length;

  // ── Données graphes ──
  const severityData  = severityDist
    ? Object.entries(severityDist)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    : countBy(allLogs, "severity");

  const radarValues = ["critical", "error", "warning", "info", "debug"].map((sev) =>
    severityDist?.[sev] ?? allLogs.filter((l) => l.severity === sev).length
  );
  const radarMax = Math.max(...radarValues, 1);
  const radarData = ["critical", "error", "warning", "info", "debug"].map((sev, i) => ({
    sev,
    count: Math.round((radarValues[i] / radarMax) * 100),
  }));

  const timelineData = (timeline?.timeline ?? []).map((p) => ({
    time: formatHour(p.timestamp),
    count: p.count,
  }));

  const lastBuckets = timelineData.slice(-6);

  const stats: { label: string; value: number; icon: any; tone: Tone }[] = [
    { label: "Total logs",      value: total,         icon: Activity,      tone: "indigo" },
    { label: "Critiques",       value: criticalCount, icon: ShieldAlert,   tone: "red"    },
    { label: "Erreurs",         value: errorCount,    icon: AlertTriangle, tone: "orange" },
    { label: "Avertissements",  value: warnCount,     icon: Clock,         tone: "amber"  },
  ];

  return (
    <div className="flex flex-col gap-6 p-1">

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="min-w-0">
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Bienvenue, {user?.username} — {user?.role}
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate("/logs")} className="shrink-0 self-start sm:self-auto">
          <FileSearch className="h-4 w-4 mr-2" />
          Voir tous les logs
        </Button>
      </motion.div>

      {/* Stat cards */}
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4"
      >
        {stats.map((s) => (
          <StatCard key={s.label} {...s} loading={loading} />
        ))}
      </motion.div>

      {/* Tabs de graphes */}
      <Tabs value={tab} onValueChange={(v) => setTab(v as typeof tab)}>
        <TabsList>
          {TABS.map(({ value, label, icon: Icon }) => (
            <TabsTrigger key={value} value={value} className="gap-1.5">
              {tab === value && (
                <motion.span
                  layoutId="dashboard-tab-pill"
                  className="absolute inset-0 rounded-md bg-background shadow-sm"
                  transition={{ type: "spring", bounce: 0.25, duration: 0.4 }}
                />
              )}
              <span className="relative z-10 flex items-center gap-1.5">
                <Icon className="h-3.5 w-3.5" />
                {label}
              </span>
            </TabsTrigger>
          ))}
        </TabsList>

        <AnimatePresence mode="wait">
          {/* Vue d'ensemble : timeline + sévérités */}
          {tab === "overview" && (
            <TabsContent value="overview" forceMount asChild>
              <motion.div
                key="overview"
                variants={panelTransition}
                initial="hidden"
                animate="show"
                exit="exit"
              >
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="show"
                  className="grid grid-cols-1 gap-4 lg:grid-cols-3"
                >
                  <div className="lg:col-span-2">
                    <ChartCard title="Activité dans le temps">
                      <AreaChart data={timelineData}>
                        <defs>
                          <linearGradient id="grad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%"  stopColor="#6366f1" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0}   />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                        <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Area type="monotone" dataKey="count" stroke="#6366f1" fill="url(#grad)" name="Logs" />
                      </AreaChart>
                    </ChartCard>
                  </div>

                  <motion.div variants={fadeUp}>
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-sm font-medium">Répartition par sévérité</CardTitle>
                      </CardHeader>
                      <CardContent className="flex flex-col items-center">
                        <ResponsiveContainer width="100%" height={180}>
                          <PieChart>
                            <Pie
                              data={severityData}
                              cx="50%" cy="50%"
                              innerRadius={45} outerRadius={75}
                              dataKey="value"
                              nameKey="name"
                              label={({ name, percent = 0 }) => `${name} ${(percent * 100).toFixed(0)}%`}
                              labelLine={false}
                              isAnimationActive
                            >
                              {severityData.map((entry) => (
                                <Cell key={entry.name} fill={SEV_COLORS[entry.name] ?? "#94a3b8"} />
                              ))}
                            </Pie>
                            <Tooltip />
                          </PieChart>
                        </ResponsiveContainer>
                        <div className="flex flex-wrap gap-2 justify-center mt-2">
                          {severityData.map((s) => (
                            <span key={s.name} className="flex items-center gap-1 text-xs">
                              <span
                                className="w-2 h-2 rounded-full inline-block"
                                style={{ background: SEV_COLORS[s.name] ?? "#94a3b8" }}
                              />
                              {s.name}
                            </span>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                </motion.div>
              </motion.div>
            </TabsContent>
          )}

          {/* Sources : top hosts + top IPs */}
          {tab === "sources" && (
            <TabsContent value="sources" forceMount asChild>
              <motion.div
                key="sources"
                variants={panelTransition}
                initial="hidden"
                animate="show"
                exit="exit"
              >
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="show"
                  className="grid grid-cols-1 gap-4 lg:grid-cols-2"
                >
                  <ChartCard title="Top hôtes sources" height={220}>
                    <BarChart data={topHosts} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={70} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#22c55e" radius={[0, 4, 4, 0]} name="Logs" isAnimationActive />
                    </BarChart>
                  </ChartCard>

                  <ChartCard title="Top IPs sources" height={220}>
                    <BarChart data={topIPs} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis type="number" tick={{ fontSize: 10 }} />
                      <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={90} />
                      <Tooltip />
                      <Bar dataKey="value" fill="#f97316" radius={[0, 4, 4, 0]} name="Logs" isAnimationActive />
                    </BarChart>
                  </ChartCard>
                </motion.div>
              </motion.div>
            </TabsContent>
          )}

          {/* Types & menace : bar types + radar */}
          {tab === "types" && (
            <TabsContent value="types" forceMount asChild>
              <motion.div
                key="types"
                variants={panelTransition}
                initial="hidden"
                animate="show"
                exit="exit"
              >
                <motion.div
                  variants={staggerContainer}
                  initial="hidden"
                  animate="show"
                  className="grid grid-cols-1 gap-4 lg:grid-cols-2"
                >
                  <ChartCard title="Logs par type" height={220}>
                    <BarChart data={typeData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                      <YAxis tick={{ fontSize: 10 }} />
                      <Tooltip />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Logs" isAnimationActive>
                        {typeData.map((entry, i) => (
                          <Cell key={entry.name} fill={TYPE_COLORS[i % TYPE_COLORS.length]} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ChartCard>

                  <ChartCard title="Radar — profil de menace" height={220}>
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="var(--border)" />
                      <PolarAngleAxis dataKey="sev" tick={{ fontSize: 11 }} />
                      <Radar name="Logs" dataKey="count" stroke="#6366f1" fill="#6366f1" fillOpacity={0.35} isAnimationActive />
                      <Tooltip />
                    </RadarChart>
                  </ChartCard>
                </motion.div>
              </motion.div>
            </TabsContent>
          )}

          {/* Tendance : line chart */}
          {tab === "trend" && (
            <TabsContent value="trend" forceMount asChild>
              <motion.div
                key="trend"
                variants={panelTransition}
                initial="hidden"
                animate="show"
                exit="exit"
              >
                <ChartCard title="Tendance récente (6 derniers intervalles)" height={220}>
                  <LineChart data={lastBuckets}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                    <YAxis tick={{ fontSize: 10 }} />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#ec4899"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      name="Logs"
                      isAnimationActive
                    />
                  </LineChart>
                </ChartCard>
              </motion.div>
            </TabsContent>
          )}
        </AnimatePresence>
      </Tabs>

      {/* Logs récents */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: 0.15 }}>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Logs récents</CardTitle>
          </CardHeader>
          <CardContent>
            <LogTable logs={logs} loading={loading} />
          </CardContent>
        </Card>
      </motion.div>

    </div>
  );
};

export default Dashboard;
