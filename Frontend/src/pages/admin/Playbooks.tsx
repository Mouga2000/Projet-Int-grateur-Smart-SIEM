// src/pages/admin/Playbooks.tsx
import { useEffect, useState } from "react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "../../components/ui/dialog";

const TRIGGERS = ["manual", "alert_created", "scheduled", "webhook"];

const Playbooks = () => {
  const [playbooks, setPlaybooks] = useState<any[]>([]);
  const [loading, setLoading]     = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing]     = useState<any>(null);
  const [form, setForm]           = useState<any>({});
  const [saving, setSaving]       = useState(false);

  // Execution
  const [executeOpen, setExecuteOpen] = useState(false);
  const [executing, setExecuting]     = useState(false);
  const [execPb, setExecPb]           = useState<any>(null);
  const [execTargetIp, setExecTargetIp] = useState("");
  const [execContext, setExecContext]  = useState(JSON.stringify({ agent_ip: "", user: "" }, null, 2));
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

  const openExecute = (pb: any) => {
    setExecPb(pb);
    setExecTargetIp("");
    setExecContext(JSON.stringify({ agent_ip: "", user: "" }, null, 2));
    setExecResult(null);
    setExecuteOpen(true);
  };

  const handleExecute = async () => {
    if (!execPb) return;
    if (!execTargetIp.trim()) return;
    setExecuting(true);
    setExecResult(null);
    try {
      let extra = {};
      try { extra = JSON.parse(execContext); } catch { extra = {}; }
      const context = { source_ip: execTargetIp.trim(), ...extra };
      const { data } = await api.post(ENDPOINTS.playbooks.execute(execPb.id), context);
      setExecResult(JSON.stringify(data, null, 2));
    } catch (e: any) {
      setExecResult(`Erreur : ${e?.response?.data?.detail ?? e.message}`);
    } finally {
      setExecuting(false);
    }
  };

  const STATUS_COLORS: Record<string, string> = {
    ACTIVE:   "text-green-400",
    INACTIVE: "text-gray-500",
    DRAFT:    "text-yellow-400",
  };

  const MODE_COLORS: Record<string, string> = {
    AUTO:    "bg-red-900/40 text-red-400 border-red-800",
    CONFIRM: "bg-yellow-900/40 text-yellow-400 border-yellow-800",
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
                <span className={`text-xs px-1.5 py-0.5 border rounded ${MODE_COLORS[pb.mode]}`}>
                  {pb.mode}
                </span>
                <span className={`text-xs ${STATUS_COLORS[pb.status]}`}>{pb.status}</span>
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
              onChange={(e) => setForm({ ...form, trigger: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              {TRIGGERS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Mode d'exécution</label>
            <div className="flex gap-2">
              {(["AUTO", "CONFIRM"] as string[]).map((m) => (
                <button
                  key={m}
                  onClick={() => setForm({ ...form, mode: m })}
                  className={`flex-1 py-1.5 rounded-lg border text-sm transition-colors ${
                    form.mode === m
                      ? m === "AUTO"
                        ? "border-red-700 bg-red-900/30 text-red-400"
                        : "border-yellow-700 bg-yellow-900/30 text-yellow-400"
                      : "border-gray-700 bg-gray-800 text-gray-400"
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
            {form.mode === "AUTO" && (
              <p className="text-xs text-red-400 mt-1">
                ⚠ Mode AUTO : les actions s'exécutent sans confirmation.
              </p>
            )}
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Statut</label>
            <select
              value={form.status ?? "DRAFT"}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              {(["DRAFT", "ACTIVE", "INACTIVE"] as string[]).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
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
                <p className="text-[11px] text-destructive">
                  L'IP de la machine à bloquer, isoler ou analyser est obligatoire.
                </p>
              )}
            </div>
            <div className="space-y-1.5">
              <Label>Contexte supplémentaire (JSON, optionnel)</Label>
              <textarea
                rows={4}
                value={execContext}
                onChange={(e) => setExecContext(e.target.value)}
                className="w-full bg-muted border rounded-md p-2 text-xs font-mono resize-none"
                placeholder='{"agent_ip": "192.168.1.50", "user": "admin"}'
              />
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
            <Button disabled={executing || !execTargetIp.trim()} onClick={handleExecute}>
              {executing ? "Exécution en cours..." : "Exécuter"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Playbooks;