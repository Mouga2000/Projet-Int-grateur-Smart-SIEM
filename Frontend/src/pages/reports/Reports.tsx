import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { ReportConfig, ReportType, ReportFormat } from "../../types/report";
import reportService from "../../services/reportService";
import { Button } from "../../components/ui/Button";

const REPORT_TYPES: ReportType[] = ["SECURITY", "AUDIT", "KPI", "INCIDENT"];
const REPORT_FORMATS: ReportFormat[] = ["PDF", "CSV", "EXCEL"];

const Reports = () => {
  const navigate = useNavigate();
  const [config, setConfig] = useState<ReportConfig>({
    type: "SECURITY",
    format: "PDF",
    period: { from: "", to: "" },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      const report = await reportService.generate(config);
      if (report.downloadUrl) {
        window.open(report.downloadUrl, "_blank");
      }
      setSuccess(true);
    } catch (err: any) {
      setError(err?.response?.data?.message ?? "Erreur lors de la génération.");
    } finally {
      setLoading(false);
    }
  };

  const isValid = config.period.from && config.period.to;

  return (
    <div className="flex max-w-xl flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold text-foreground">Génération de rapports</h1>
        <p className="text-sm text-muted-foreground">Configurez et générez vos rapports de sécurité.</p>
      </div>

      <div className="flex flex-col gap-4 rounded-xl border border-border bg-card p-6 text-card-foreground shadow-sm">
        <div>
          <label className="mb-1 block text-xs text-muted-foreground">Type de rapport</label>
          <select
            value={config.type}
            onChange={(e) => setConfig({ ...config, type: e.target.value as ReportType })}
            className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            {REPORT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-xs text-muted-foreground">Format</label>
          <div className="flex gap-2">
            {REPORT_FORMATS.map((f) => (
              <button
                key={f}
                onClick={() => setConfig({ ...config, format: f })}
                className={`rounded-lg border px-4 py-1.5 text-sm transition-colors ${
                  config.format === f
                    ? "border-primary bg-primary/10 text-foreground"
                    : "border-input bg-background text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">Du</label>
            <input
              type="date"
              value={config.period.from}
              onChange={(e) => setConfig({ ...config, period: { ...config.period, from: e.target.value } })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">Au</label>
            <input
              type="date"
              value={config.period.to}
              onChange={(e) => setConfig({ ...config, period: { ...config.period, to: e.target.value } })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="scheduled"
            checked={config.scheduled ?? false}
            onChange={(e) => setConfig({ ...config, scheduled: e.target.checked })}
            className="accent-primary"
          />
          <label htmlFor="scheduled" className="text-sm text-muted-foreground">
            Planifier l'envoi automatique
          </label>
        </div>

        {config.scheduled && (
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">Fréquence</label>
            <select
              value={config.scheduleInterval ?? "WEEKLY"}
              onChange={(e) => setConfig({ ...config, scheduleInterval: e.target.value as any })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="DAILY">Quotidien</option>
              <option value="WEEKLY">Hebdomadaire</option>
              <option value="MONTHLY">Mensuel</option>
            </select>
          </div>
        )}

        {error && <p className="text-xs text-destructive">{error}</p>}
        {success && <p className="text-xs text-green-600 dark:text-green-400">Rapport généré avec succès.</p>}

        <div className="flex gap-3 pt-2">
          <Button variant="default" disabled={!isValid || loading} onClick={handleGenerate}>
            {loading ? "Génération..." : "Générer le rapport"}
          </Button>
          <Button variant="ghost" onClick={() => navigate("/reports/export")}>
            Export données →
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Reports;
