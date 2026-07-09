// src/pages/archive/Archive.tsx
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import archiveService from "../../services/archiveService";
import type { Archive as ArchiveType } from "@/types/archive";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Plus, Link2, ShieldCheck, ShieldX, Loader2, Archive as ArchiveIcon } from "lucide-react";

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
  show: { transition: { staggerChildren: 0.05 } },
};

const Archive = () => {
  const navigate = useNavigate();
  const [archives, setArchives] = useState<ArchiveType[]>([]);
  const [loading, setLoading]   = useState(true);
  const [days, setDays]         = useState(90);
  const [windowDays, setWindowDays] = useState(30);
  const [creating, setCreating] = useState(false);
  const [verifying, setVerifying] = useState<number | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);

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
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-6"
    >
      {/* Header */}
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold">Archives certifiées</h1>
          <p className="text-sm text-muted-foreground">Archivage conforme avec chaîne de hachage et signature RSA.</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => navigate("/archive/chain")}>
          <Link2 className="h-4 w-4 mr-2" />
          Voir la chaîne
        </Button>
      </motion.div>

      {/* Création */}
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }}>
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
              <motion.span
                animate={creating ? { rotate: 360 } : { rotate: 0 }}
                transition={creating ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
                className="mr-2 inline-flex"
              >
                {creating ? <Loader2 className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
              </motion.span>
              {creating ? "Création..." : "Créer l'archive"}
            </Button>
          </CardContent>
          <AnimatePresence>
            {createError && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <CardContent className="pt-0">
                  <p className="text-xs text-destructive">{createError}</p>
                </CardContent>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>
      </motion.div>

      {/* Loading */}
      <AnimatePresence>
        {loading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center justify-center py-12 text-muted-foreground gap-2 text-sm"
          >
            <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      {!loading && (
        <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }}>
          <Card>
            <CardContent className="pt-6">
              {archives.length === 0 ? (
                <div className="flex flex-col items-center gap-2 py-8 text-center">
                  <ArchiveIcon className="h-8 w-8 text-muted-foreground/40" />
                  <p className="text-sm text-muted-foreground">Aucune archive créée.</p>
                </div>
              ) : (
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
                            <AnimatePresence mode="wait">
                              <motion.span
                                key={a.status}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.9 }}
                                transition={{ duration: 0.15 }}
                                className="inline-block"
                              >
                                <Badge variant="outline" className={STATUS_STYLES[a.status] ?? ""}>{a.status}</Badge>
                              </motion.span>
                            </AnimatePresence>
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
                              <motion.span
                                animate={verifying === a.id ? { rotate: 360 } : { rotate: 0 }}
                                transition={verifying === a.id ? { duration: 0.8, repeat: Infinity, ease: "linear" } : { duration: 0.2 }}
                                className="mr-2 inline-flex"
                              >
                                {verifying === a.id ? (
                                  <Loader2 className="h-4 w-4" />
                                ) : a.status === "compromised" ? (
                                  <ShieldX className="h-4 w-4 text-destructive" />
                                ) : (
                                  <ShieldCheck className="h-4 w-4" />
                                )}
                              </motion.span>
                              Vérifier
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </motion.div>
      )}
    </motion.div>
  );
};

export default Archive;