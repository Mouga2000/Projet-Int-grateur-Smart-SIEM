import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { Plus, Loader2, ScrollText, Power, Pencil, Trash2, Braces, X } from "lucide-react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";
import { cn } from "../../lib/utils";

interface Rule { id: string; name: string; description: string; severity: string; enabled: boolean; condition: string; rule_type?: string; }

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-red-500/10 text-red-700 border-red-200 dark:text-red-300 dark:border-red-900/60",
  high: "bg-orange-500/10 text-orange-700 border-orange-200 dark:text-orange-300 dark:border-orange-900/60",
  medium: "bg-yellow-500/10 text-yellow-700 border-yellow-200 dark:text-yellow-300 dark:border-yellow-900/60",
  low: "bg-blue-500/10 text-blue-700 border-blue-200 dark:text-blue-300 dark:border-blue-900/60",
  info: "bg-muted text-muted-foreground border-border",
};

const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const staggerContainer = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const rowItem = { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0 } };

function AnimatedDialog({ open, onOpenChange, title, children }: { open: boolean; onOpenChange: (open: boolean) => void; title: string; children: React.ReactNode; }) {
  return (
    <DialogPrimitive.Root open={open} onOpenChange={onOpenChange}>
      <AnimatePresence>
        {open && (
          <DialogPrimitive.Portal forceMount>
            <DialogPrimitive.Overlay asChild forceMount>
              <motion.div className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
            </DialogPrimitive.Overlay>
            <DialogPrimitive.Content asChild forceMount>
              <motion.div className="fixed left-1/2 top-1/2 z-50 max-h-[85vh] w-full max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-border bg-card p-6 text-card-foreground shadow-xl" initial={{ opacity: 0, scale: 0.96, y: 8 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.96, y: 8 }}>
                <div className="mb-4 flex items-center justify-between">
                  <DialogPrimitive.Title className="text-base font-semibold text-foreground">{title}</DialogPrimitive.Title>
                  <DialogPrimitive.Close className="text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></DialogPrimitive.Close>
                </div>
                {children}
              </motion.div>
            </DialogPrimitive.Content>
          </DialogPrimitive.Portal>
        )}
      </AnimatePresence>
    </DialogPrimitive.Root>
  );
}

export default function Rules() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Rule | null>(null);
  const [form, setForm] = useState<Partial<Rule>>({});
  const [saving, setSaving] = useState(false);
  const [fieldError, setFieldError] = useState("");

  useEffect(() => { (async () => { setLoading(true); try { const { data } = await api.get(ENDPOINTS.rules.list); setRules(data); } finally { setLoading(false); } })(); }, []);

  const openCreate = () => { setEditing(null); setForm({ enabled: true, severity: "medium", rule_type: "single_event", condition: "" }); setFieldError(""); setModalOpen(true); };
  const openEdit = (rule: Rule) => { setEditing(rule); setForm(rule); setFieldError(""); setModalOpen(true); };
  const handleSave = async () => {
    if (!form.name?.trim()) return setFieldError("Le nom est obligatoire.");
    setSaving(true);
    try {
      const payload = { ...form };
      if (typeof payload.condition === "string") { try { payload.condition = JSON.parse(payload.condition); } catch { payload.condition = ""; } }
      if (editing) { const { data } = await api.patch(ENDPOINTS.rules.update(editing.id), payload); setRules((p) => p.map((r) => r.id === data.id ? data : r)); }
      else { const { data } = await api.post(ENDPOINTS.rules.create, payload); setRules((p) => [...p, data]); }
      setModalOpen(false);
    } finally { setSaving(false); }
  };
  const toggleEnabled = async (rule: Rule) => { const { data } = await api.patch(ENDPOINTS.rules.update(rule.id), { enabled: !rule.enabled }); setRules((p) => p.map((r) => r.id === data.id ? data : r)); };
  const handleDelete = async (id: string) => { setRules((p) => p.filter((r) => r.id !== id)); await api.delete(ENDPOINTS.rules.delete(id)); };

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="flex flex-col gap-5">
      <motion.div variants={fadeUp} className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-foreground">Règles de corrélation</h1>
          {!loading && <p className="mt-0.5 text-xs text-muted-foreground">{rules.length} règle{rules.length > 1 ? "s" : ""}</p>}
        </div>
        <Button size="sm" onClick={openCreate}><Plus className="mr-1.5 h-4 w-4" />Créer une règle</Button>
      </motion.div>

      {loading && <div className="flex items-center justify-center gap-2 py-12 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" />Chargement...</div>}
      {!loading && rules.length === 0 && <div className="flex flex-col items-center gap-2 py-12 text-center"><ScrollText className="h-8 w-8 text-muted-foreground/40" /><p className="text-sm text-muted-foreground">Aucune règle configurée.</p></div>}

      {!loading && rules.length > 0 && (
        <motion.div variants={staggerContainer} className="flex flex-col gap-2">
          <AnimatePresence mode="popLayout">
            {rules.map((rule) => (
              <motion.div key={rule.id} layout variants={rowItem} className="flex items-start justify-between gap-4 rounded-xl border border-border bg-card p-4">
                <div className="min-w-0 flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className={cn("h-2 w-2 rounded-full", rule.enabled ? "bg-green-500" : "bg-muted-foreground")} />
                    <p className="truncate text-sm font-medium text-foreground">{rule.name}</p>
                    <span className={cn("shrink-0 rounded border px-1.5 py-0.5 text-xs", SEVERITY_STYLES[rule.severity] ?? SEVERITY_STYLES.info)}>{rule.severity}</span>
                  </div>
                  {rule.description && <p className="truncate pl-4 text-xs text-muted-foreground">{rule.description}</p>}
                  {rule.condition && <span className="flex items-center gap-1 pl-4"><Braces className="size-3 text-primary/60" /><code className="truncate font-mono text-xs text-primary">{typeof rule.condition === "string" ? rule.condition : JSON.stringify(rule.condition)}</code></span>}
                </div>
                <div className="flex shrink-0 items-center gap-1">
                  <IconAction label={rule.enabled ? "Désactiver" : "Activer"} icon={Power} tone={rule.enabled ? "text-green-600 dark:text-green-400" : "text-muted-foreground"} onClick={() => toggleEnabled(rule)} />
                  <IconAction label="Modifier" icon={Pencil} tone="text-primary" onClick={() => openEdit(rule)} />
                  <IconAction label="Supprimer" icon={Trash2} tone="text-red-600 dark:text-red-400" onClick={() => handleDelete(rule.id)} />
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </motion.div>
      )}

      <AnimatedDialog open={modalOpen} onOpenChange={setModalOpen} title={editing ? "Modifier la règle" : "Créer une règle"}>
        <div className="flex flex-col gap-4">
          <div className="space-y-1.5"><Label>Nom <span className="text-destructive">*</span></Label><Input value={form.name ?? ""} onChange={(e) => { setForm({ ...form, name: e.target.value }); setFieldError(""); }} placeholder="Brute Force Detection" /></div>
          <div className="space-y-1.5"><Label>Description</Label><Input value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Description de la règle..." /></div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Type de règle</label>
              <select value={form.rule_type ?? "single_event"} onChange={(e) => setForm({ ...form, rule_type: e.target.value })} className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50">
                <option value="single_event">Single Event</option><option value="threshold">Threshold</option><option value="sequence">Sequence</option><option value="correlation">Correlation</option><option value="ueba">UEBA</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Sévérité</label>
              <select value={form.severity ?? "medium"} onChange={(e) => setForm({ ...form, severity: e.target.value })} className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50">
                <option value="critical">Critique</option><option value="high">Haute</option><option value="medium">Moyenne</option><option value="low">Basse</option><option value="info">Info</option>
              </select>
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">Condition (JSON)</label>
            <p className="mb-1 text-[10px] text-muted-foreground">Ex: {"{\"field\": \"severity\", \"value\": \"critical\"}"}</p>
            <textarea rows={3} value={typeof form.condition === "object" ? JSON.stringify(form.condition, null, 2) : (form.condition ?? "")} onChange={(e) => setForm({ ...form, condition: e.target.value })} className="w-full resize-none rounded-lg border border-input bg-background px-3 py-2 font-mono text-sm text-foreground placeholder:text-muted-foreground outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50" placeholder='{"field": "raw_message", "value": "Failed password"}' />
          </div>
          <div className="flex items-center gap-2"><input type="checkbox" id="enabled" checked={form.enabled ?? true} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} className="accent-primary" /><label htmlFor="enabled" className="text-sm text-muted-foreground">Activer la règle</label></div>
          {fieldError && <p className="text-xs text-destructive">{fieldError}</p>}
          <div className="flex justify-end gap-2 pt-2"><Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>Annuler</Button><Button disabled={saving || !form.name?.trim()} onClick={handleSave}>{saving ? "Enregistrement..." : editing ? "Enregistrer" : "Créer"}</Button></div>
        </div>
      </AnimatedDialog>
    </motion.div>
  );
}

function IconAction({ label, icon: Icon, tone, onClick }: { label: string; icon: any; tone: string; onClick: () => void }) {
  return <button type="button" onClick={onClick} title={label} className={cn("flex size-7 items-center justify-center rounded-lg transition-colors hover:bg-muted", tone)}><Icon className="size-3.5" /></button>;
}
