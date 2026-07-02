// src/pages/audit/Verify.tsx
import { useEffect, useState } from "react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { Loader2, CheckCircle2, XCircle, Link2 } from "lucide-react";

interface Archive {
  id: number;
  date_from: string;
  date_to: string;
  log_count: number;
  chain_hash: string;
  previous_hash: string | null;
  status: string;
  certified_at: string;
  file_path?: string;
  file_hash?: string;
}

interface VerifyResult {
  archive_id: number;
  valid: boolean;
  checks: { name: string; ok: boolean; detail?: string }[];
}

interface ChainEntry {
  id: number;
  period: string;
  logs: number;
  chain_hash: string;
  previous_hash: string;
  status: string;
  certified_at: string;
}

const STATUS_STYLES: Record<string, string> = {
  certified:   "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  verified:    "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
  compromised: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
};

const Verify = () => {
  const [archives, setArchives] = useState<Archive[]>([]);
  const [loading, setLoading] = useState(true);
  const [chain, setChain] = useState<ChainEntry[]>([]);
  const [chainLoading, setChainLoading] = useState(false);
  const [showChain, setShowChain] = useState(false);

  // Résultat de vérification
  const [verifyingId, setVerifyingId] = useState<number | null>(null);
  const [verifyResult, setVerifyResult] = useState<VerifyResult | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  const fetchArchives = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(ENDPOINTS.archive.list, { params: { page: 1, size: 50 } });
      setArchives(data.items ?? []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchArchives(); }, []);

  const handleVerify = async (archiveId: number) => {
    setVerifyingId(archiveId);
    setVerifyResult(null);
    setVerifyError(null);
    try {
      const { data } = await api.post(ENDPOINTS.archive.verify(archiveId));
      setVerifyResult(data);
    } catch {
      setVerifyError("Erreur lors de la vérification.");
    } finally {
      setVerifyingId(null);
    }
  };

  const loadChain = async () => {
    setChainLoading(true);
    try {
      const { data } = await api.get(ENDPOINTS.archive.chain);
      setChain(data.chain ?? []);
      setShowChain(true);
    } finally {
      setChainLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16 text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Vérification des archives</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Vérifie l'intégrité des archives et leur chaîne de custody.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadChain} disabled={chainLoading}>
          <Link2 className="h-4 w-4 mr-1.5" />
          {chainLoading ? "Chargement..." : "Afficher la chaîne"}
        </Button>
      </div>

      {/* Chaîne */}
      {showChain && chain.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Link2 className="h-4 w-4" />
              Chaîne de custody ({chain.length} maillons)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col gap-1 text-xs font-mono">
              {chain.map((entry, i) => (
                <div key={entry.id} className="flex items-center gap-3 p-2 rounded-md hover:bg-muted/30">
                  <span className="text-muted-foreground w-6 shrink-0">#{i + 1}</span>
                  <span className="w-40 shrink-0 text-foreground">{entry.period}</span>
                  <Badge className={STATUS_STYLES[entry.status] ?? ""} variant="outline">{entry.status}</Badge>
                  <span className="text-muted-foreground truncate" title={entry.chain_hash}>
                    Hash: {entry.chain_hash}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Résultat de vérification */}
      {verifyResult && (
        <Card className={verifyResult.valid ? "border-green-500/30" : "border-red-500/30"}>
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              {verifyResult.valid
                ? <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                : <XCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
              }
              <div className="flex-1">
                <p className={`text-sm font-medium ${verifyResult.valid ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                  Archive #{verifyResult.archive_id} — {verifyResult.valid ? "Intègre" : "Compromise"}
                </p>
                <div className="flex flex-col gap-1 mt-2 text-xs">
                  {verifyResult.checks?.map((check, i) => (
                    <div key={i} className="flex items-center gap-2">
                      {check.ok
                        ? <span className="text-green-500">✓</span>
                        : <span className="text-red-500">✗</span>
                      }
                      <span className="text-muted-foreground">{check.name}</span>
                      {check.detail && <span className="text-muted-foreground/60">— {check.detail}</span>}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {verifyError && (
        <Card className="border-red-500/30">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{verifyError}</p>
          </CardContent>
        </Card>
      )}

      {/* Liste des archives */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            Archives disponibles ({archives.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {archives.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4 text-center">
              Aucune archive créée. Les archives sont générées automatiquement ou via la page Archives.
            </p>
          ) : (
            <div className="flex flex-col gap-2">
              {archives.map((arc) => (
                <div key={arc.id} className="border rounded-lg p-3 flex items-center justify-between gap-4 hover:border-primary/30 transition-colors">
                  <div className="flex flex-col gap-1 min-w-0">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-medium">Archive #{arc.id}</span>
                      <Badge className={STATUS_STYLES[arc.status] ?? ""} variant="outline">{arc.status}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {arc.date_from?.slice(0, 10)} → {arc.date_to?.slice(0, 10)} · {arc.log_count} logs
                    </p>
                    {arc.chain_hash && (
                      <p className="text-[11px] font-mono text-muted-foreground truncate">
                        SHA-256: {arc.chain_hash}
                      </p>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={verifyingId === arc.id}
                    onClick={() => handleVerify(arc.id)}
                  >
                    {verifyingId === arc.id ? "Vérification..." : "Vérifier"}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Verify;
