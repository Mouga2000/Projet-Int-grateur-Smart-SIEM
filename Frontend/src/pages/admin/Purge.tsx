// src/pages/admin/Purge.tsx
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as AlertDialogPrimitive from "@radix-ui/react-alert-dialog";
import adminService from "@/services/adminService";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { Trash2, CheckCircle2, Info, ShieldAlert } from "lucide-react";

// ─── Motion presets ──────────────────────────────────────────────────────────

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
};

const staggerContainer = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

// ─── AlertDialog animé (Radix + framer-motion) ──────────────────────────────
// Le <AlertDialog> shadcn anime en CSS via data-state, pas en motion.
// On repasse directement par les primitives Radix avec forceMount +
// AnimatePresence pour une vraie animation motion de confirmation destructive.

function AnimatedAlertDialog({
  trigger, title, description, onConfirm, confirmLabel = "Confirmer",
}: {
  trigger: React.ReactNode;
  title: string;
  description: string;
  onConfirm: () => void;
  confirmLabel?: string;
}) {
  const [open, setOpen] = useState(false);

  return (
    <AlertDialogPrimitive.Root open={open} onOpenChange={setOpen}>
      <AlertDialogPrimitive.Trigger asChild>{trigger}</AlertDialogPrimitive.Trigger>
      <AnimatePresence>
        {open && (
          <AlertDialogPrimitive.Portal forceMount>
            <AlertDialogPrimitive.Overlay asChild forceMount>
              <motion.div
                className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
              />
            </AlertDialogPrimitive.Overlay>
            <AlertDialogPrimitive.Content asChild forceMount>
              <motion.div
                initial={{ opacity: 0, scale: 0.96, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.96, y: 8 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-2xl border bg-background p-6 shadow-lg"
              >
                <div className="mb-2 flex items-center gap-2">
                  <div className="flex size-8 items-center justify-center rounded-full bg-destructive/10 text-destructive">
                    <ShieldAlert className="size-4" />
                  </div>
                  <AlertDialogPrimitive.Title className="text-base font-semibold">
                    {title}
                  </AlertDialogPrimitive.Title>
                </div>
                <AlertDialogPrimitive.Description className="text-sm text-muted-foreground">
                  {description}
                </AlertDialogPrimitive.Description>

                <div className="mt-5 flex justify-end gap-2">
                  <AlertDialogPrimitive.Cancel asChild>
                    <Button variant="ghost">Annuler</Button>
                  </AlertDialogPrimitive.Cancel>
                  <AlertDialogPrimitive.Action asChild>
                    <Button variant="destructive" onClick={onConfirm}>{confirmLabel}</Button>
                  </AlertDialogPrimitive.Action>
                </div>
              </motion.div>
            </AlertDialogPrimitive.Content>
          </AlertDialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </AlertDialogPrimitive.Root>
  );
}

// ─── Bandeau d'info animé (remplace <Alert>) ─────────────────────────────────

function InfoBanner({ tone, icon: Icon, children }: { tone: "info" | "success"; icon: any; children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "flex items-start gap-2 overflow-hidden rounded-xl border px-4 py-3 text-sm",
        tone === "success" ? "border-green-500/30 bg-green-500/10 text-green-600" : "border-border bg-muted/40 text-foreground"
      )}
    >
      <Icon className="mt-0.5 size-4 shrink-0" />
      <div>{children}</div>
    </motion.div>
  );
}

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
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-6 max-w-xl"
    >
      <motion.h1 variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="text-lg font-semibold">
        Rétention des données
      </motion.h1>

      <AnimatePresence>
        {config && (
          <InfoBanner tone="info" icon={Info}>
            Rétention actuelle : logs {config.log_retention_days}j, audits {config.audit_retention_days}j.
            Purge automatique : {config.next_purge}
          </InfoBanner>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {result && (
          <InfoBanner tone="success" icon={CheckCircle2}>
            {result}
          </InfoBanner>
        )}
      </AnimatePresence>

      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }}>
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
            <AnimatedAlertDialog
              trigger={
                <Button variant="destructive" className="self-start" disabled={loading}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Purger les logs
                </Button>
              }
              title="Confirmer la purge"
              description={`Cette action supprimera définitivement tous les logs de plus de ${logDays} jours. Irréversible.`}
              onConfirm={handlePurgeLogs}
            />
          </CardContent>
        </Card>
      </motion.div>

      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }}>
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
            <AnimatedAlertDialog
              trigger={
                <Button variant="destructive" className="self-start" disabled={loading}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Purger les audits
                </Button>
              }
              title="Confirmer la purge"
              description={`Cette action supprimera définitivement tous les audits de plus de ${auditDays} jours. Irréversible.`}
              onConfirm={handlePurgeAudit}
            />
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Purge;