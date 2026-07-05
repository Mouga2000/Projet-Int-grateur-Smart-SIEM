// src/pages/admin/Playbooks.tsx
import { useEffect, useState } from "react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";
import type { Playbook } from "../../types/playbook";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "../../components/ui/dialog";

const TRIGGERS: Playbook["trigger"][] = ["manual", "alert_created", "scheduled", "webhook"];

const emptyForm: Partial<Playbook> = {
  name: "",
  description: "",
  trigger: "manual",
  enabled: true,
  steps: [],
  variables: {},
  timeout_seconds: 300,
  max_retries: 3,
};

const Playbooks = () => {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [loading, setLoading]     = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing]     = useState<Playbook | null>(null);
  const [form, setForm]           = useState<Partial<Playbook>>(emptyForm);
  const [saving, setSaving]       = useState(false);

  // Execution
  const [executeOpen, setExecuteOpen] = useState(false);
  const [executing, setExecuting]     = useState(false);
  const [execPb, setExecPb]           = useState<Playbook | null>(null);
  const [execTargetIp, setExecTargetIp] = useState("");
  const [execAgentIp, setExecAgentIp]   = useState("");
  const [execUsername, setExecUsername] = useState("");
  const [execAgents, setExecAgents]     = useState<any[]>([]);
  const [execResult, setExecResult]   = useState<string | null>(null);

  const fetchPlaybooks = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(ENDPOINTS.playbooks.list);
      setPlaybooks(data ?? []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPlaybooks(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ enabled: true, trigger: "manual", steps: [], variables: {} });
    setModalOpen(true);
  };

  const openEdit = (pb: any) => {
    setEditing(pb);
    setForm(pb);
    setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing) {
        const { data: updated } = await api.put(`/api/v1/playbooks/${editing.id}`, form);
        setPlaybooks((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      } else {
        const { data: created } = await api.post("/api/v1/playbooks/", form);
        setPlaybooks((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    await api.delete(`/api/v1/playbooks/${id}`);
    setPlaybooks((prev) => prev.filter((p) => p.id !== id));
  };

  const openExecute = async (pb: any) => {
    setExecPb(pb);
    setExecTargetIp("");
    setExecAgentIp("");
    setExecUsername("");
    setExecResult(null);
    setExecuteOpen(true);
    try {
      const { data } = await api.get("/agents/");
      setExecAgents(data ?? []);
    } catch {
      setExecAgents([]);
    }
  };

  const handleExecute = async () => {
    if (!execPb) return;
    if (!execTargetIp.trim() || !execAgentIp.trim()) return;
    setExecuting(true);
    setExecResult(null);
    try {
      const context = { source_ip: execTargetIp.trim(), agent_ip: execAgentIp.trim(), user: execUsername.trim() };
      const { data } = await api.post(ENDPOINTS.playbooks.execute(execPb.id), context);
      setExecResult(JSON.stringify(data, null, 2));
    } catch (e: any) {
      setExecResult(`Erreur : ${e?.response?.data?.detail ?? e.message}`);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-white font-medium text-lg">Playbooks SOAR</h1>
        <Button size="sm" onClick={openCreate}>
          + Créer un playbook
        </Button>
      </div>

      {loading && <p className="text-gray-500 text-sm">Chargement...</p>}

      <div className="flex flex-col gap-2">
        {playbooks.map((pb) => (
          <div
            key={pb.id}
            className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-start justify-between gap-4"
          >
            <div className="flex flex-col gap-1.5 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className="text-sm text-white font-medium">{pb.name}</p>
                {pb.enabled === false && (
                  <span className="text-xs text-gray-500">(désactivé)</span>
                )}
              </div>
              <p className="text-xs text-gray-500">{pb.description}</p>
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <span>Déclencheur : <span className="text-gray-400">{pb.trigger}</span></span>
                <span>·</span>
                <span>{(pb.steps?.length ?? 0)} étape(s)</span>
              </div>
            </div>
            <div className="flex gap-2 shrink-0 items-center">
              <button
                onClick={() => openExecute(pb)}
                className="text-xs text-green-400 hover:text-green-300 transition-colors"
              >
                 Exécuter
              </button>
              <button
                onClick={() => openEdit(pb)}
                className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                Modifier
              </button>
              <button
                onClick={() => handleDelete(pb.id)}
                className="text-xs text-red-400 hover:text-red-300 transition-colors"
              >
                Supprimer
              </button>
            </div>
          </div>
        ))}
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? "Modifier le playbook" : "Créer un playbook"}
      >
        <div className="flex flex-col gap-4">
          <div className="space-y-1.5">
            <Label>Nom</Label>
            <Input value={form.name ?? ""} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Block Brute Force" />
          </div>
          <div className="space-y-1.5">
            <Label>Description</Label>
            <Input value={form.description ?? ""} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Déclencheur</label>
            <select
              value={form.trigger ?? "manual"}
              onChange={(e) => setForm({ ...form, trigger: e.target.value as Playbook["trigger"] })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              {TRIGGERS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="flex items-center gap-2 pb-1">
            <input
              type="checkbox"
              id="pb-enabled"
              checked={form.enabled ?? true}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
              className="accent-cyan-500"
            />
            <label htmlFor="pb-enabled" className="text-xs text-gray-400">Playbook actif</label>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>Annuler</Button>
            <Button disabled={saving} onClick={handleSave}>
              {saving ? "Enregistrement..." : editing ? "Enregistrer" : "Créer"}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Dialog d'exécution */}
      <Dialog open={executeOpen} onOpenChange={setExecuteOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Exécuter le playbook : {execPb?.name}</DialogTitle>
          </DialogHeader>
          <div className="flex flex-col gap-4">
            <div className="space-y-1.5">
              <Label className="font-medium">
                IP de la machine cible <span className="text-destructive">*</span>
              </Label>
              <Input
                value={execTargetIp}
                onChange={(e) => setExecTargetIp(e.target.value)}
                placeholder="10.0.0.5"
              />
              {!execTargetIp.trim() && (
                <p className="text-[11px] text-destructive">IP de la machine à bloquer, isoler ou analyser.</p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label className="font-medium">
                Nom d'utilisateur
              </Label>
              <Input
                value={execUsername}
                onChange={(e) => setExecUsername(e.target.value)}
                placeholder="admin, bstoll... (optionnel)"
              />
              <p className="text-[11px] text-muted-foreground">Requis uniquement pour les actions de désactivation de compte.</p>
            </div>
            <div className="space-y-1.5">
              <Label className="font-medium">
                Agent <span className="text-destructive">*</span>
              </Label>
              {execAgents.length > 0 ? (
                <select
                  value={execAgentIp}
                  onChange={(e) => setExecAgentIp(e.target.value)}
                  className="flex h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm text-white [&>option]:text-black"
                >
                  <option value="">Sélectionner un agent...</option>
                  {execAgents.map((a: any) => (
                    <option key={a.id} value={a.ip_address}>
                      {a.hostname} ({a.ip_address}) — {a.operating_system || "?"}
                    </option>
                  ))}
                </select>
              ) : (
                <Input
                  value={execAgentIp}
                  onChange={(e) => setExecAgentIp(e.target.value)}
                  placeholder="192.168.1.50"
                />
              )}
              {!execAgentIp.trim() && (
                <p className="text-[11px] text-destructive">Machine qui exécute les actions (blocage, isolation...).</p>
              )}
              {execAgents.length > 0 && (
                <p className="text-[11px] text-muted-foreground">Ou saisis une IP manuellement si l'agent n'est pas listé.</p>
              )}
            </div>
            {execResult && (
              <div className="space-y-1.5">
                <Label>Résultat</Label>
                <pre className="bg-muted border rounded-md p-2 text-xs overflow-x-auto whitespace-pre-wrap">
                  {execResult}
                </pre>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setExecuteOpen(false)}>Fermer</Button>
            <Button disabled={executing || !execTargetIp.trim() || !execAgentIp.trim()} onClick={handleExecute}>
              {executing ? "Exécution en cours..." : "Exécuter"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Playbooks;