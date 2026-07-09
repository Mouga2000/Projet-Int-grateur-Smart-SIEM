// src/pages/reports/ExportData.tsx
import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import type { ReportConfig, ReportFormat } from "../../types/report";
import reportService from "../../services/reportService";
import { Button } from "../../components/ui/Button";
import { Card, CardContent } from "../../components/ui/card";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";
import { cn } from "../../lib/utils";

const ExportData = () => {
  const [format, setFormat] = useState<ReportFormat>("CSV");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `export-${from}-${to}.${format.toLowerCase()}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError("Erreur lors de l'export.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex max-w-md flex-col gap-6">
      <div>
        <h1 className="text-lg font-medium">Export de donnees</h1>
        <p className="text-sm text-muted-foreground">Exportez les donnees brutes de securite.</p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 pt-6">
          <div>
            <Label className="mb-1 block text-xs">Format</Label>
            <div className="flex gap-2">
              {(["CSV", "EXCEL"] as ReportFormat[]).map((f) => (
                <button
                  key={f}
                  type="button"
                  onClick={() => setFormat(f)}
                  className={cn(
                    "rounded-lg border px-4 py-1.5 text-sm transition-colors",
                    format === f
                      ? "border-primary bg-primary/10 text-foreground"
                      : "border-input text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label className="mb-1 block text-xs">Du</Label>
              <Input type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
            </div>
            <div>
              <Label className="mb-1 block text-xs">Au</Label>
              <Input type="date" value={to} onChange={(e) => setTo(e.target.value)} />
            </div>
          </div>

          {error && <p className="text-xs text-destructive">{error}</p>}

          <Button className="self-start" disabled={!from || !to || loading} onClick={handleExport}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
            Telecharger l'export
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExportData;
