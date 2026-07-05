// src/pages/dashboard/Dashboard.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import api from "../../services/api";
import logService from "../../services/logService";
import type { LogEntry, TimelineResponse } from "../../types/log";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";

// Cache timeline 30s entre les refreshes du Dashboard
let _timelineCache: { data: TimelineResponse; ts: number } | null = null;
import { Button } from "../../components/ui/Button";
import LogTable from "../../components/logs/LogTable";
import {
  FileSearch, AlertTriangle, Activity, Clock,
  ShieldAlert, Database, TrendingUp, Wifi,
} from "lucide-react";
import {
  AreaChart, Area,
  BarChart, Bar,
  PieChart, Pie, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
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
    // Inclure le jour pour différencier les dates dans le graphique
    return d.toLocaleDateString("fr-FR", { day: "2-digit", month: "2-digit" })
      + " " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  }
  catch { return ts; }
}

// ─── Composant stat card ─────────────────────────────────────────────────────

function StatCard({
  label, value, icon: Icon, color, loading,
}: { label: string; value: string | number; icon: any; color: string; loading: boolean }) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-muted-foreground mb-1">{label}</p>
            <p className="text-2xl font-bold">{loading ? "…" : value}</p>
          </div>
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
      </CardContent>
    </Card>
  );
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [logs, setLogs]         = useState<LogEntry[]>([]);
  const [allLogs, setAllLogs]     = useState<LogEntry[]>([]);
  const [timeline, setTimeline]   = useState<TimelineResponse | null>(null);
  const [severityDist, setSeverityDist] = useState<Record<string, number> | null>(null);
  const [topHosts, setTopHosts]   = useState<{ name: string; value: number }[]>([]);
  const [topIPs, setTopIPs]       = useState<{ name: string; value: number }[]>([]);
  const [typeData, setTypeData]   = useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchAll = async () => {
      try {
        // Étape 1 : logs récents (rapide)
        const recent = await logService.list(1, 10);
        if (cancelled) return;
        setLogs(recent.items);

        // Étape 2 : logs pour les métriques (taille réduite)
        const full = await logService.list(1, 50);
        if (cancelled) return;
        setAllLogs(full.items);

        // Étape 2b : répartition des sévérités (tous les logs via agrégation)
        try {
          const dist = await api.get("/logs/severity-distribution");
          if (!cancelled) setSeverityDist(dist.data);
        } catch {} // Ignorer si l'endpoint échoue

        // Étape 2c : top hosts, top IPs & types (via agrégations)
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

        // Étape 3 : timeline avec cache 30s
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

  // Radar: sévérités normalisées (via agrégation ES, en %)
  const radarValues = ["critical", "error", "warning", "info", "debug"].map((sev) =>
    severityDist?.[sev] ?? allLogs.filter((l) => l.severity === sev).length
  );
  const radarMax = Math.max(...radarValues, 1);
  const radarData = ["critical", "error", "warning", "info", "debug"].map((sev, i) => ({
    sev,
    count: Math.round((radarValues[i] / radarMax) * 100),
  }));

  // Timeline avec formatage
  const timelineData = (timeline?.timeline ?? []).map((p) => ({
    time: formatHour(p.timestamp),
    count: p.count,
  }));

  // Trend par type × heure (simplifié : 6 derniers buckets)
  const lastBuckets = timelineData.slice(-6);

  const stats = [
    { label: "Total logs",   value: total,         icon: Activity,     color: "text-blue-500"     },
    { label: "Critiques",    value: criticalCount,  icon: ShieldAlert,  color: "text-red-500"      },
    { label: "Erreurs",      value: errorCount,     icon: AlertTriangle,color: "text-orange-500"   },
    { label: "Avertissements", value: warnCount,    icon: Clock,        color: "text-yellow-500"   },
  ];

  return (
    <div className="flex flex-col gap-6 p-1">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">
            Bienvenue, {user?.username} — {user?.role}
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate("/logs")}>
          <FileSearch className="h-4 w-4 mr-2" />
          Voir tous les logs
        </Button>
      </div>

      {/*  */}
      <div className="grid grid-cols-2 gap-3">
        {stats.map((s) => (
          <StatCard key={s.label} {...s} loading={loading} />
        ))}
      </div>

      {/* Row 1 — Timeline + Sévérités (donut) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-sm font-medium">Activité dans le temps</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
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
            </ResponsiveContainer>
          </CardContent>
        </Card>

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
                  <span className="w-2 h-2 rounded-full inline-block" style={{ background: SEV_COLORS[s.name] ?? "#94a3b8" }} />
                  {s.name}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Row 2 — Top Hôtes + Top IPs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Top hôtes sources</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topHosts} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={70} />
                <Tooltip />
                <Bar dataKey="value" fill="#22c55e" radius={[0, 4, 4, 0]} name="Logs" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Top IPs sources</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={topIPs} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 10 }} />
                <YAxis dataKey="name" type="category" tick={{ fontSize: 10 }} width={90} />
                <Tooltip />
                <Bar dataKey="value" fill="#f97316" radius={[0, 4, 4, 0]} name="Logs" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Row 3 — Types de logs (bar) + Radar sévérités */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Logs par type</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]} name="Logs">
                  {typeData.map((entry, i) => (
                    <Cell key={entry.name} fill={TYPE_COLORS[i % TYPE_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Radar — profil de menace</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width="100%" height={200}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--border)" />
                <PolarAngleAxis dataKey="sev" tick={{ fontSize: 11 }} />
                <Radar name="Logs" dataKey="count" stroke="#6366f1" fill="#6366f1" fillOpacity={0.35} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Row 4 — Tendance (line) */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Tendance récente (6 derniers intervalles)</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={lastBuckets}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#ec4899" strokeWidth={2} dot={{ r: 4 }} name="Logs" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Logs récents */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Logs récents</CardTitle>
        </CardHeader>
        <CardContent>
          <LogTable logs={logs} loading={loading} />
        </CardContent>
      </Card>

    </div>
  );
};

export default Dashboard;