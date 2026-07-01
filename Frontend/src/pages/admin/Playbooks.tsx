// src/pages/admin/Playbooks.tsx
import { useEffect, useState } from "react";
import type { Playbook, PlaybookMode, PlaybookStatus, PlaybookTrigger } from "../../types/playbook";
import adminService from "../../services/adminService";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import Input from "../../components/ui/Input";

const TRIGGERS: PlaybookTrigger[] = ["ALERT_CRITICAL", "ALERT_HIGH", "LOGIN_FAILED", "ANOMALY", "CUSTOM"];

const Playbooks = () => {
  const [playbooks, setPlaybooks] = useState<Playbook[]>([]);
  const [loading, setLoading]     = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing]     = useState<Playbook | null>(null);
  const [form, setForm]           = useState<Partial<Playbook>>({});
  const [saving, setSaving]       = useState(false);

  const fetchPlaybooks = async () => {
    setLoading(true);
    try {
      const data = await adminService.getPlaybooks();
      setPlaybooks(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchPlaybooks(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm({ mode: "CONFIRM", status: "DRAFT", actions: [] });
    setModalOpen(true);
  };

  const openEdit = (pb: Playbook) => {
    setEditing(pb);
    setForm(pb);
    setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      if (editing) {
        const updated = await adminService.updatePlaybook(editing.id, form);
        setPlaybooks((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      } else {
        const created = await adminService.createPlaybook(form);
        setPlaybooks((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    await adminService.deletePlaybook(id);
    setPlaybooks((prev) => prev.filter((p) => p.id !== id));
  };

  const STATUS_COLORS: Record<PlaybookStatus, string> = {
    ACTIVE:   "text-green-400",
    INACTIVE: "text-gray-500",
    DRAFT:    "text-yellow-400",
  };

  const MODE_COLORS: Record<PlaybookMode, string> = {
    AUTO:    "bg-red-900/40 text-red-400 border-red-800",
    CONFIRM: "bg-yellow-900/40 text-yellow-400 border-yellow-800",
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-white font-medium text-lg">Playbooks SOAR</h1>
        <Button variant="primary" size="sm" onClick={openCreate}>
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
                <span>{pb.actions.length} action{pb.actions.length > 1 ? "s" : ""}</span>
              </div>
            </div>
            <div className="flex gap-2 shrink-0">
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
          <Input
            label="Nom"
            value={form.name ?? ""}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Block Brute Force"
          />
          <Input
            label="Description"
            value={form.description ?? ""}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <div>
            <label className="text-xs text-gray-400 block mb-1">Déclencheur</label>
            <select
              value={form.trigger ?? "ALERT_CRITICAL"}
              onChange={(e) => setForm({ ...form, trigger: e.target.value as PlaybookTrigger })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              {TRIGGERS.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Mode d'exécution</label>
            <div className="flex gap-2">
              {(["AUTO", "CONFIRM"] as PlaybookMode[]).map((m) => (
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
              onChange={(e) => setForm({ ...form, status: e.target.value as PlaybookStatus })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
            >
              {(["DRAFT", "ACTIVE", "INACTIVE"] as PlaybookStatus[]).map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>Annuler</Button>
            <Button variant="primary" size="sm" loading={saving} onClick={handleSave}>
              {editing ? "Enregistrer" : "Créer"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Playbooks;