// src/pages/archive/ArchiveChain.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import archiveService from "../../services/archiveService";
import type { ArchiveChainEntry } from "../../types/archive";
import { Card, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/badge";
import { ArrowLeft, ShieldCheck, ShieldX } from "lucide-react";

const STATUS_STYLES: Record<string, string> = {
  certified:   "status-certified",
  verified:    "status-verified",
  compromised: "status-compromised",
};

const ArchiveChain = () => {
  const navigate = useNavigate();
  const [chain, setChain]       = useState<ArchiveChainEntry[]>([]);
  const [integrity, setIntegrity] = useState<string>("");
  const [loading, setLoading]   = useState(true);

  useEffect(() => {
    archiveService.getChain()
      .then((data) => {
        setChain(data.chain);
        setIntegrity(data.integrity);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <Button variant="ghost" size="sm" className="self-start" onClick={() => navigate("/archive")}>
        <ArrowLeft className="h-4 w-4 mr-2" />
        Retour aux archives
      </Button>

      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Chaîne d'intégrité cryptographique</h1>
        <Badge variant="outline" className={integrity === "verified" ? "status-verified" : integrity === "empty" ? "status-empty" : "status-compromised"}>
          {integrity === "verified" ? (
            <ShieldCheck className="h-3 w-3 mr-1" />
          ) : (
            <ShieldX className="h-3 w-3 mr-1" />
          )}
          {integrity}
        </Badge>
      </div>

      {loading && <p className="text-sm text-muted-foreground">Chargement...</p>}
      {!loading && chain.length === 0 && (
        <p className="text-sm text-muted-foreground">Aucune archive dans la chaîne.</p>
      )}

      <div className="relative pl-6">
        <div className="absolute left-2 top-0 bottom-0 w-px bg-border" />
        <div className="space-y-3">
          {chain.map((entry, idx) => (
            <Card key={entry.id} className="relative">
              <div className="absolute -left-[1.85rem] top-6 w-3 h-3 rounded-full bg-primary border-2 border-background" />
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Archive #{entry.id}</p>
                  <Badge variant="outline" className={STATUS_STYLES[entry.status] ?? "status-empty"}>
                    {entry.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mb-2">{entry.period} · {entry.logs} logs</p>
                <div className="flex flex-col gap-1 text-xs">
                  <div className="flex items-center gap-1 font-mono text-muted-foreground break-all">
                    <span className="shrink-0 text-[10px]">Précédent:</span>
                    <code className="bg-muted/50 px-1 rounded text-[11px]">{entry.previous_hash}</code>
                  </div>
                  <div className="flex items-center gap-1 font-mono text-foreground break-all">
                    <span className="shrink-0 text-[10px] text-muted-foreground">Courant:</span>
                    <code className="bg-muted px-1 rounded text-[11px] font-semibold">{entry.chain_hash}</code>
                    <span
                      className="text-[10px] text-muted-foreground cursor-pointer hover:text-foreground shrink-0"
                      onClick={() => navigator.clipboard.writeText(entry.chain_hash)}
                      title="Copier le hash"
                    >
                      📋
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Certifié le {new Date(entry.certified_at).toLocaleString("fr-FR")}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ArchiveChain;