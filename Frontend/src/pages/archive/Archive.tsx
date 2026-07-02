// src/pages/archive/Archive.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import archiveService from "../../services/archiveService";
import type { Archive as ArchiveType } from "@/types/archive";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Plus, Link2, ShieldCheck, ShieldX } from "lucide-react";

const STATUS_STYLES: Record<string, string> = {
  certified:   "status-certified",
  verified:    "status-verified",
  compromised: "status-compromised",
};

const Archive = () => {
  const navigate = useNavigate();
  const [archives, setArchives] = useState<ArchiveType[]>([]);
  const [loading, setLoading]   = useState(true);
  const [days, setDays]         = useState(90);
  const [windowDays, setWindowDays] = useState(30);
  const [creating, setCreating] = useState(false);
  const [verifying, setVerifying] = useState<number | null>(null);

  const fetchArchives = async () => {
    setLoading(true);
    try {
      const data = await archiveService.list();
      setArchives(data.items);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchArchives(); }, []);

  const [createError, setCreateError] = useState<string | null>(null);

  const handleCreate = async () => {
    setCreating(true);
    setCreateError(null);
    try {
      await archiveService.create(days, windowDays);
      fetchArchives();
    } catch (err: any) {
      const msg = err?.response?.data?.detail ?? err?.message ?? "Erreur lors de la création";
      setCreateError(typeof msg === "string" ? msg : "Période sans logs à archiver");
    } finally {
      setCreating(false);
    }
  };

  const handleVerify = async (id: number) => {
    setVerifying(id);
    try {
      const result = await archiveService.verify(id);
      setArchives((prev) =>
        prev.map((a) => (a.id === id ? { ...a, status: result.valid ? "verified" : "compromised" } : a))
      );
    } finally {
      setVerifying(null);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Archives certifiées</h1>
          <p className="text-sm text-muted-foreground">Archivage conforme avec chaîne de hachage et signature RSA.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate("/archive/chain")}>
          <Link2 className="h-4 w-4 mr-2" />
          Voir la chaîne
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Créer une nouvelle archive</CardTitle>
          <CardDescription>Archive les logs plus anciens que N jours sur une fenêtre temporelle donnée.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="space-y-1.5">
            <Label>Âge minimum (jours)</Label>
            <Input type="number" value={Number.isNaN(days) ? "" : days} onChange={(e) => setDays(parseInt(e.target.value) || 90)} className="w-32" />
          </div>
          <div className="space-y-1.5">
            <Label>Fenêtre (jours)</Label>
            <Input type="number" value={Number.isNaN(windowDays) ? "" : windowDays} onChange={(e) => setWindowDays(parseInt(e.target.value) || 30)} className="w-32" />
          </div>
          <Button onClick={handleCreate} disabled={creating}>
            <Plus className="h-4 w-4 mr-2" />
            {creating ? "Création..." : "Créer l'archive"}
          </Button>
        </CardContent>
        {createError && (
          <CardContent className="pt-0">
            <p className="text-xs text-destructive">{createError}</p>
          </CardContent>
        )}
      </Card>

      {loading ? (
        <p className="text-sm text-muted-foreground">Chargement...</p>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Période</TableHead>
                  <TableHead>Logs</TableHead>
                  <TableHead>Statut</TableHead>
                  <TableHead>Certifié le</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {archives.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-mono text-xs">{a.id}</TableCell>
                    <TableCell className="text-xs">
                      {new Date(a.date_from).toLocaleDateString("fr-FR")} → {new Date(a.date_to).toLocaleDateString("fr-FR")}
                    </TableCell>
                    <TableCell>{a.log_count}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className={STATUS_STYLES[a.status] ?? ""}>{a.status}</Badge>
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(a.certified_at).toLocaleString("fr-FR")}
                    </TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={verifying === a.id}
                        onClick={() => handleVerify(a.id)}
                      >
                        {a.status === "compromised" ? (
                          <ShieldX className="h-4 w-4 mr-2 text-destructive" />
                        ) : (
                          <ShieldCheck className="h-4 w-4 mr-2" />
                        )}
                        Vérifier
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Archive;