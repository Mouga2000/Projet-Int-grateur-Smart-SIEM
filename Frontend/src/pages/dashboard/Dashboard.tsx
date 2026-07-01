// src/pages/dashboard/Dashboard.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import logService from "../../services/logService";
import type { LogEntry, TimelineResponse } from "../../types/log";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
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

function topN<T>(arr: T[], key: keyof T, n = 5) {
  return countBy(arr, key).slice(0, n);
}

function formatHour(ts: string) {
  try { return new Date(ts).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }); }
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
  const [allLogs, setAllLogs]   = useState<LogEntry[]>([]);
  const [timeline, setTimeline] = useState<TimelineResponse | null>(null);
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    Promise.all([
      logService.list(1, 10),
      logService.list(1, 200),
      logService.timeline({ interval: "1h" }),
    ])
      .then(([recent, full, tl]) => {
        setLogs(recent.items);
        setAllLogs(full.items);
        setTimeline(tl);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // ── Métriques ──
  const criticalCount = allLogs.filter((l) => l.severity === "critical").length;
  const errorCount    = allLogs.filter((l) => l.severity === "error").length;
  const warnCount     = allLogs.filter((l) => l.severity === "warning").length;
  const total         = timeline?.total ?? allLogs.length;

  // ── Données graphes ──
  const severityData  = countBy(allLogs, "severity");
  const typeData      = countBy(allLogs, "log_type");
  const topHosts      = topN(allLogs, "host", 6);
  const topIPs        = topN(allLogs, "source_ip", 6);

  // Radar: sévérités normalisées
  const radarData = ["critical","error","warning","info","debug"].map((sev) => ({
    sev,
    count: allLogs.filter((l) => l.severity === sev).length,
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