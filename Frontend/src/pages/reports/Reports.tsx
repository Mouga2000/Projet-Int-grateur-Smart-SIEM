// src/pages/reports/Reports.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { ReportConfig, ReportType, ReportFormat } from "../../types/report";
import reportService from "../../services/reportService";
import Button from "../../components/ui/Button";

const REPORT_TYPES: ReportType[]   = ["SECURITY", "AUDIT", "KPI", "INCIDENT"];
const REPORT_FORMATS: ReportFormat[] = ["PDF", "CSV", "EXCEL"];

const Reports = () => {
  const navigate = useNavigate();
  const [config, setConfig] = useState<ReportConfig>({
    type:   "SECURITY",
    format: "PDF",
    period: { from: "", to: "" },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
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
    <div className="flex flex-col gap-6 max-w-xl">
      <div>
        <h1 className="text-white font-medium text-lg">Génération de rapports</h1>
        <p className="text-gray-500 text-sm">Configurez et générez vos rapports de sécurité.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col gap-4">
        {/* Type */}
        <div>
          <label className="text-xs text-gray-400 block mb-1">Type de rapport</label>
          <select
            value={config.type}
            onChange={(e) => setConfig({ ...config, type: e.target.value as ReportType })}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
          >
            {REPORT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        {/* Format */}
        <div>
          <label className="text-xs text-gray-400 block mb-1">Format</label>
          <div className="flex gap-2">
            {REPORT_FORMATS.map((f) => (
              <button
                key={f}
                onClick={() => setConfig({ ...config, format: f })}
                className={`px-4 py-1.5 rounded-lg border text-sm transition-colors ${
                  config.format === f
                    ? "border-cyan-600 bg-cyan-900/30 text-cyan-400"
                    : "border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        {/* Période */}
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Du</label>
            <input
              type="date"
              value={config.period.from}
              onChange={(e) => setConfig({ ...config, period: { ...config.period, from: e.target.value } })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Au</label>
            <input
              type="date"
              value={config.period.to}
              onChange={(e) => setConfig({ ...config, period: { ...config.period, to: e.target.value } })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Planification */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="scheduled"
            checked={config.scheduled ?? false}
            onChange={(e) => setConfig({ ...config, scheduled: e.target.checked })}
            className="accent-cyan-500"
          />
          <label htmlFor="scheduled" className="text-sm text-gray-400">
            Planifier l'envoi automatique
          </label>
        </div>

        {config.scheduled && (
          <div>
            <label className="text-xs text-gray-400 block mb-1">Fréquence</label>
            <select
              value={config.scheduleInterval ?? "WEEKLY"}
              onChange={(e) => setConfig({ ...config, scheduleInterval: e.target.value as any })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              <option value="DAILY">Quotidien</option>
              <option value="WEEKLY">Hebdomadaire</option>
              <option value="MONTHLY">Mensuel</option>
            </select>
          </div>
        )}

        {error   && <p className="text-red-400 text-xs">{error}</p>}
        {success && <p className="text-green-400 text-xs">Rapport généré avec succès.</p>}

        <div className="flex gap-3 pt-2">
          <Button
            variant="primary"
            disabled={!isValid}
            loading={loading}
            onClick={handleGenerate}
          >
            Générer le rapport
          </Button>
          <Button
            variant="ghost"
            onClick={() => navigate("/reports/export")}
          >
            Export données →
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Reports;