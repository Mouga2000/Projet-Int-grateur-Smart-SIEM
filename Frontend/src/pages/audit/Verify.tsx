// src/pages/audit/Verify.tsx
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Badge } from "../../components/ui/badge";
import { cn } from "../../lib/utils";
import { Loader2, CheckCircle2, XCircle, Link2, Archive as ArchiveIcon, Check, X } from "lucide-react";

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
  certified:   "status-certified",
  verified:    "status-verified",
  compromised: "status-compromised",
};

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
};

const rowItem = {
  hidden: { opacity: 0, y: 8 },
  show: { opacity: 1, y: 0 },
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
    if (showChain) { setShowChain(false); return; }
    setChainLoading(true);
    try {
      const { data } = await api.get(ENDPOINTS.archive.chain);
      setChain(data.chain ?? []);
      setShowChain(true);
    } finally {
      setChainLoading(false);
    }
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-6"
    >
      {/* Header */}
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Vérification des archives</h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Vérifie l'intégrité des archives et leur chaîne de custody.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={loadChain} disabled={chainLoading}>
          <motion.span
            animate={chainLoading ? { rotate: 360 } : { rotate: 0 }}
            transition={chainLoading ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
            className="mr-1.5 inline-flex"
          >
            <Link2 className="h-4 w-4" />
          </motion.span>
          {chainLoading ? "Chargement..." : showChain ? "Masquer la chaîne" : "Afficher la chaîne"}
        </Button>
      </motion.div>

      {/* Loading initial */}
      <AnimatePresence>
        {loading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center justify-center py-16 text-muted-foreground gap-2"
          >
            <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
          </motion.div>
        )}
      </AnimatePresence>

      {!loading && (
        <>
          {/* Chaîne */}
          <AnimatePresence>
            {showChain && chain.length > 0 && (
              <motion.div
                key="chain"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
                className="overflow-hidden"
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Link2 className="h-4 w-4" />
                      Chaîne de custody ({chain.length} maillons)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <motion.div
                      variants={staggerContainer}
                      initial="hidden"
                      animate="show"
                      className="flex flex-col gap-1 text-xs font-mono"
                    >
                      {chain.map((entry, i) => (
                        <motion.div key={entry.id} variants={rowItem} className="flex items-center gap-3 p-2 rounded-md">
                          <span className="text-muted-foreground w-6 shrink-0">#{i + 1}</span>
                          <span className="w-40 shrink-0 text-foreground">{entry.period}</span>
                          <Badge className={STATUS_STYLES[entry.status] ?? ""} variant="outline">{entry.status}</Badge>
                          <span className="text-muted-foreground truncate" title={entry.chain_hash}>
                            Hash: {entry.chain_hash}
                          </span>
                        </motion.div>
                      ))}
                    </motion.div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Résultat de vérification */}
          <AnimatePresence mode="wait">
            {verifyResult && (
              <motion.div
                key={verifyResult.archive_id}
                initial={{ opacity: 0, y: -8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
              >
                <Card className={verifyResult.valid ? "border-green-500/30" : "border-red-500/30"}>
                  <CardContent className="pt-6">
                    <div className="flex items-start gap-3">
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", bounce: 0.4, duration: 0.4, delay: 0.1 }}
                      >
                        {verifyResult.valid
                          ? <CheckCircle2 className="h-5 w-5 text-green-500 mt-0.5 shrink-0" />
                          : <XCircle className="h-5 w-5 text-red-500 mt-0.5 shrink-0" />
                        }
                      </motion.span>
                      <div className="flex-1">
                        <p className={cn(
                          "text-sm font-medium",
                          verifyResult.valid ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
                        )}>
                          Archive #{verifyResult.archive_id} — {verifyResult.valid ? "Intègre" : "Compromise"}
                        </p>
                        <motion.div
                          variants={staggerContainer}
                          initial="hidden"
                          animate="show"
                          className="flex flex-col gap-1 mt-2 text-xs"
                        >
                          {verifyResult.checks?.map((check, i) => (
                            <motion.div key={i} variants={rowItem} className="flex items-center gap-2">
                              {check.ok
                                ? <Check className="h-3 w-3 text-green-500" />
                                : <X className="h-3 w-3 text-red-500" />
                              }
                              <span className="text-muted-foreground">{check.name}</span>
                              {check.detail && <span className="text-muted-foreground/60">— {check.detail}</span>}
                            </motion.div>
                          ))}
                        </motion.div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence>
            {verifyError && (
              <motion.div
                key="verify-error"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <Card className="border-red-500/30">
                  <CardContent className="pt-6">
                    <p className="text-sm text-destructive">{verifyError}</p>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Liste des archives */}
          <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }}>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">
                  Archives disponibles ({archives.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {archives.length === 0 ? (
                  <div className="flex flex-col items-center gap-2 py-8 text-center">
                    <ArchiveIcon className="h-8 w-8 text-muted-foreground/40" />
                    <p className="text-sm text-muted-foreground">
                      Aucune archive créée. Les archives sont générées automatiquement ou via la page Archives.
                    </p>
                  </div>
                ) : (
                  <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    animate="show"
                    className="flex flex-col gap-2"
                  >
                    {archives.map((arc) => (
                      <motion.div
                        key={arc.id}
                        variants={rowItem}
                        className="border rounded-lg p-3 flex items-center justify-between gap-4"
                      >
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
                          <motion.span
                            animate={verifyingId === arc.id ? { rotate: 360 } : { rotate: 0 }}
                            transition={verifyingId === arc.id ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
                            className="mr-1.5 inline-flex"
                          >
                            {verifyingId === arc.id && <Loader2 className="h-3.5 w-3.5" />}
                          </motion.span>
                          {verifyingId === arc.id ? "Vérification..." : "Vérifier"}
                        </Button>
                      </motion.div>
                    ))}
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}
    </motion.div>
  );
};

export default Verify;
