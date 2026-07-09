import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { Plus, Loader2, Siren, Play, Pencil, Trash2, X, Zap } from "lucide-react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";
import { cn } from "../../lib/utils";
import type { Playbook } from "../../types/playbook";

const TRIGGERS: Playbook["trigger"][] = ["manual", "alert_created", "scheduled", "webhook"];
const emptyForm: Partial<Playbook> = { name: "", description: "", trigger: "manual", enabled: true, steps: [], variables: {}, timeout_seconds: 300, max_retries: 3 };
const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const staggerContainer = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const rowItem = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } };

function AnimatedDialog({ open, onOpenChange, title, children, maxWidth = "max-w-lg" }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; children: React.ReactNode; maxWidth?: string; }) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <DialogPrimitive.Portal forceMount>
            <DialogPrimitive.Overlay asChild forceMount><motion.div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} /></DialogPrimitive.Overlay>
            <DialogPrimitive.Content asChild forceMount>
              <motion.div className={cn("fixed left-1/2 top-1/2 z-50 max-h-[85vh] w-full -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-border bg-card p-6 text-card-foreground shadow-xl", maxWidth)} initial={{ opacity: 0, scale: 0.96, y: 8 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.96, y: 8 }}>
                <div className="mb-4 flex items-center justify-between"><DialogPrimitive.Title className="text-base font-semibold text-foreground">{title}</DialogPrimitive.Title><DialogPrimitive.Close className="text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></DialogPrimitive.Close></div>
                {children}
              </motion.div>
            </DialogPrimitive.Content>
          </DialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </DialogPrimitive.Root>
  );
}

export default function Playbooks() {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Playbook | null>(null);
  const [form, setForm] = useState<Partial<Playbook>>(emptyForm);
  const [saving, setSaving] = useState(false);
  const [executeOpen, setExecuteOpen] = useState(false);
  const [executing, setExecuting] = useState(false);
  const [execPb, setExecPb] = useState<Playbook | null>(null);
  const [execTargetIp, setExecTargetIp] = useState("");
  const [execAgentIp, setExecAgentIp] = useState("");
  const [execUsername, setExecUsername] = useState("");
  const [execAgents, setExecAgents] = useState<any[]>([]);
  const [execResult, setExecResult] = useState<string | null>(null);

  const fetchPlaybooks = async () => { setLoading(true); try { const { data } = await api.get(ENDPOINTS.playbooks.list); setPlaybooks(data ?? []); } finally { setLoading(false); } };
  useEffect(() => { fetchPlaybooks(); }, []);
  const openCreate = () => { setEditing(null); setForm({ enabled: true, trigger: "manual", steps: [], variables: {} }); setModalOpen(true); };
  const openEdit = (pb: Playbook) => { setEditing(pb); setForm(pb); setModalOpen(true); };
  const handleSave = async () => { setSaving(true); try { if (editing) { const { data } = await api.put(`/api/v1/playbooks/${editing.id}`, form); setPlaybooks((p) => p.map((x) => x.id === data.id ? data : x)); } else { const { data } = await api.post("/api/v1/playbooks/", form); setPlaybooks((p) => [...p, data]); } setModalOpen(false); } finally { setSaving(false); } };
  const handleDelete = async (id: number) => { setPlaybooks((p) => p.filter((x) => x.id !== id)); await api.delete(`/api/v1/playbooks/${id}`); };
  const openExecute = async (pb: Playbook) => { setExecPb(pb); setExecTargetIp(""); setExecAgentIp(""); setExecUsername(""); setExecResult(null); setExecuteOpen(true); try { const { data } = await api.get("/agents/"); setExecAgents(data ?? []); } catch { setExecAgents([]); } };
  const handleExecute = async () => { if (!execPb || !execTargetIp.trim() || !execAgentIp.trim()) return; setExecuting(true); setExecResult(null); try { const context = { source_ip: execTargetIp.trim(), agent_ip: execAgentIp.trim(), user: execUsername.trim() }; const { data } = await api.post(ENDPOINTS.playbooks.execute(execPb.id), context); setExecResult(JSON.stringify(data, null, 2)); } catch (e: any) { setExecResult(`Erreur : ${e?.response?.data?.detail ?? e.message}`); } finally { setExecuting(false); } };

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="flex flex-col gap-5">
      <motion.div variants={fadeUp} className="flex items-center justify-between">
        <div><h1 className="text-lg font-semibold text-foreground">Playbooks SOAR</h1>{!loading && <p className="mt-0.5 text-xs text-muted-foreground">{playbooks.length} playbook{playbooks.length > 1 ? "s" : ""}</p>}</div>
        <Button size="sm" onClick={openCreate}><Plus className="mr-1.5 h-4 w-4" />Créer un playbook</Button>
      </motion.div>

      {loading && <div className="flex items-center justify-center gap-2 py-12 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" />Chargement...</div>}
      {!loading && playbooks.length === 0 && <div className="flex flex-col items-center gap-2 py-12 text-center"><Siren className="h-8 w-8 text-muted-foreground/40" /><p className="text-sm text-muted-foreground">Aucun playbook configuré.</p></div>}

      {!loading && playbooks.length > 0 && <motion.div variants={staggerContainer} className="flex flex-col gap-2">{playbooks.map((pb) => <motion.div key={pb.id} layout variants={rowItem} className="flex items-start justify-between gap-4 rounded-xl border border-border bg-card p-4"><div className="flex min-w-0 items-start gap-3"><div className={cn("mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg", pb.enabled !== false ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground")}><Zap className="size-4" /></div><div className="min-w-0 flex flex-col gap-1.5"><div className="flex flex-wrap items-center gap-2"><p className="text-sm font-medium text-foreground">{pb.name}</p>{pb.enabled === false && <span className="rounded border border-border bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">Désactivé</span>}</div><p className="text-xs text-muted-foreground">{pb.description}</p><div className="flex items-center gap-2 text-xs text-muted-foreground"><span className="rounded-full bg-muted px-2 py-0.5">{pb.trigger}</span><span>{(pb.steps?.length ?? 0)} étape(s)</span></div></div></div><div className="flex shrink-0 items-center gap-1"><IconAction label="Exécuter" icon={Play} tone="text-green-600 dark:text-green-400" onClick={() => openExecute(pb)} /><IconAction label="Modifier" icon={Pencil} tone="text-primary" onClick={() => openEdit(pb)} /><IconAction label="Supprimer" icon={Trash2} tone="text-red-600 dark:text-red-400" onClick={() => handleDelete(pb.id)} /></div></motion.div>)}</motion.div>}

      <AnimatedDialog open={modalOpen} onOpenChange={setModalOpen} title={editing ? "Modifier le playbook" : "Créer un playbook"}>
        <div className="flex flex-col gap-4">
          <div className="space-y-1.5"><Label>Nom</Label><Input value={form.name ?? ""} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Block Brute Force" /></div>
          <div className="space-y-1.5"><Label>Description</Label><Input value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div><label className="mb-1 block text-xs text-muted-foreground">Déclencheur</label><select value={form.trigger ?? "manual"} onChange={(e) => setForm({ ...form, trigger: e.target.value as Playbook["trigger"] })} className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50">{TRIGGERS.map((t) => <option key={t} value={t}>{t}</option>)}</select></div>
          <div className="flex items-center gap-2 pb-1"><input type="checkbox" id="pb-enabled" checked={form.enabled ?? true} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} className="accent-primary" /><label htmlFor="pb-enabled" className="text-xs text-muted-foreground">Playbook actif</label></div>
          <div className="flex justify-end gap-2 pt-2"><Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>Annuler</Button><Button disabled={saving} onClick={handleSave}>{saving ? "Enregistrement..." : editing ? "Enregistrer" : "Créer"}</Button></div>
        </div>
      </AnimatedDialog>

      <AnimatedDialog open={executeOpen} onOpenChange={setExecuteOpen} title={`Exécuter le playbook : ${execPb?.name ?? ""}`}>
        <div className="flex flex-col gap-4">
          <div className="space-y-1.5"><Label>IP de la machine cible</Label><Input value={execTargetIp} onChange={(e) => setExecTargetIp(e.target.value)} placeholder="10.0.0.5" /></div>
          <div className="space-y-1.5"><Label>Nom d'utilisateur</Label><Input value={execUsername} onChange={(e) => setExecUsername(e.target.value)} placeholder="admin, bstoll... (optionnel)" /><p className="text-[11px] text-muted-foreground">Requis uniquement pour les actions de désactivation de compte.</p></div>
          <div className="space-y-1.5"><Label>Agent</Label>{execAgents.length > 0 ? <select value={execAgentIp} onChange={(e) => setExecAgentIp(e.target.value)} className="w-full rounded-lg border border-input bg-background px-2.5 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"><option value="">Sélectionner un agent...</option>{execAgents.map((a: any) => <option key={a.id} value={a.ip_address}>{a.hostname} ({a.ip_address}) — {a.operating_system || "?"}</option>)}</select> : <Input value={execAgentIp} onChange={(e) => setExecAgentIp(e.target.value)} placeholder="192.168.1.50" />}{execAgents.length > 0 && <p className="text-[11px] text-muted-foreground">Ou saisis une IP manuellement si l'agent n'est pas listé.</p>}</div>
          {execResult && <div className="space-y-1.5"><Label>Résultat</Label><pre className="overflow-x-auto whitespace-pre-wrap rounded-md border border-border bg-muted p-2 font-mono text-xs text-foreground">{execResult}</pre></div>}
          <div className="flex justify-end gap-2 pt-2"><Button variant="ghost" onClick={() => setExecuteOpen(false)}>Fermer</Button><Button disabled={executing || !execTargetIp.trim() || !execAgentIp.trim()} onClick={handleExecute}>{executing ? "Exécution en cours..." : "Exécuter"}</Button></div>
        </div>
      </AnimatedDialog>
    </motion.div>
  );
}

function IconAction({ label, icon: Icon, tone, onClick }: { label: string; icon: any; tone: string; onClick: () => void }) { return <button type="button" onClick={onClick} title={label} className={cn("flex size-7 items-center justify-center rounded-lg transition-colors hover:bg-muted", tone)}><Icon className="size-3.5" /></button>; }
