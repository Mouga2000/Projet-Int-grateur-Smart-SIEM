// src/pages/admin/Purge.tsx
import { useEffect, useState } from "react";
import adminService from "@/services/adminService";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Trash2, CheckCircle2 } from "lucide-react";

const Purge = () => {
  const [config, setConfig] = useState<{ log_retention_days: number; audit_retention_days: number; next_purge: string } | null>(null);
  const [logDays, setLogDays]     = useState(90);
  const [auditDays, setAuditDays] = useState(365);
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState<string | null>(null);

  useEffect(() => {
    adminService.getRetentionConfig().then((data) => {
      setConfig(data);
      setLogDays(data.log_retention_days);
      setAuditDays(data.audit_retention_days);
    });
  }, []);

  const handlePurgeLogs = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await adminService.purgeLogs(logDays);
      setResult(res.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePurgeAudit = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await adminService.purgeAudit(auditDays);
      setResult(res.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-xl">
      <h1 className="text-lg font-semibold">Rétention des données</h1>

      {config && (
        <Alert>
          <AlertDescription>
            Rétention actuelle : logs {config.log_retention_days}j, audits {config.audit_retention_days}j.
            Purge automatique : {config.next_purge}
          </AlertDescription>
        </Alert>
      )}

      {result && (
        <Alert>
          <CheckCircle2 className="h-4 w-4" />
          <AlertDescription>{result}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Purger les logs</CardTitle>
          <CardDescription>Supprime les logs Elasticsearch plus anciens que N jours.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="space-y-1.5">
            <Label>Jours de rétention</Label>
            <Input type="number" value={logDays} onChange={(e) => setLogDays(parseInt(e.target.value))} />
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className="self-start" disabled={loading}>
                <Trash2 className="h-4 w-4 mr-2" />
                Purger les logs
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Confirmer la purge</AlertDialogTitle>
                <AlertDialogDescription>
                  Cette action supprimera définitivement tous les logs de plus de {logDays} jours. Irréversible.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={handlePurgeLogs}>Confirmer</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Purger les audits</CardTitle>
          <CardDescription>Supprime les logs d'audit PostgreSQL plus anciens que N jours.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          <div className="space-y-1.5">
            <Label>Jours de rétention</Label>
            <Input type="number" value={auditDays} onChange={(e) => setAuditDays(parseInt(e.target.value))} />
          </div>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="destructive" className="self-start" disabled={loading}>
                <Trash2 className="h-4 w-4 mr-2" />
                Purger les audits
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Confirmer la purge</AlertDialogTitle>
                <AlertDialogDescription>
                  Cette action supprimera définitivement tous les audits de plus de {auditDays} jours. Irréversible.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Annuler</AlertDialogCancel>
                <AlertDialogAction onClick={handlePurgeAudit}>Confirmer</AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </CardContent>
      </Card>
    </div>
  );
};

export default Purge;