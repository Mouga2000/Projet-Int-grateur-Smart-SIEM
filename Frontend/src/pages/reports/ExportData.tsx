// src/pages/reports/ExportData.tsx
import { useState } from "react";
import type { ReportConfig, ReportFormat } from "../../types/report";
import reportService from "../../services/reportService";
import Button from "../../components/ui/Button";

const ExportData = () => {
  const [format, setFormat]   = useState<ReportFormat>("CSV");
  const [from, setFrom]       = useState("");
  const [to, setTo]           = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    try {
      const config: ReportConfig = {
        type: "SECURITY",
        format,
        period: { from, to },
      };
      const blob = await reportService.export(config);
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `export-${from}-${to}.${format.toLowerCase()}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError("Erreur lors de l'export.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-md">
      <div>
        <h1 className="text-white font-medium text-lg">Export de données</h1>
        <p className="text-gray-500 text-sm">Exportez les données brutes de sécurité.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col gap-4">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Format</label>
          <div className="flex gap-2">
            {(["CSV", "EXCEL"] as ReportFormat[]).map((f) => (
              <button
                key={f}
                onClick={() => setFormat(f)}
                className={`px-4 py-1.5 rounded-lg border text-sm transition-colors ${
                  format === f
                    ? "border-cyan-600 bg-cyan-900/30 text-cyan-400"
                    : "border-gray-700 bg-gray-800 text-gray-400 hover:border-gray-600"
                }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Du</label>
            <input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Au</label>
            <input
              type="date"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {error && <p className="text-red-400 text-xs">{error}</p>}

        <Button
          variant="primary"
          disabled={!from || !to}
          loading={loading}
          onClick={handleExport}
        >
          Télécharger l'export
        </Button>
      </div>
    </div>
  );
};

export default ExportData;