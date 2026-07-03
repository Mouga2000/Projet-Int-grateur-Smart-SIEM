// src/pages/admin/Rules.tsx
import { useEffect, useState } from "react";
import api from "../../services/api";
import { ENDPOINTS } from "../../config/endpoints";
import { Button } from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { Label } from "../../components/ui/label";

interface Rule {
  id: string;
  name: string;
  description: string;
  severity: string;
  enabled: boolean;
  condition: string;
}

const Rules = () => {
  const [rules, setRules]       = useState<Rule[]>([]);
  const [loading, setLoading]   = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing]   = useState<Rule | null>(null);
  const [form, setForm]         = useState<Partial<Rule>>({});
  const [saving, setSaving]     = useState(false);

  useEffect(() => {
    let ignore = false;
    (async () => {
      setLoading(true);
      try {
        const { data } = await api.get(ENDPOINTS.rules.list);
        if (!ignore) setRules(data);
      } finally {
        if (!ignore) setLoading(false);
      }
    })();
    return () => { ignore = true; };
  }, []);

  const [fieldError, setFieldError] = useState("");

  const openCreate = () => {
    setEditing(null);
    setForm({ enabled: true, severity: "medium", rule_type: "single_event", condition: {} });
    setFieldError("");
    setModalOpen(true);
  };

  const openEdit = (rule: Rule) => {
    setEditing(rule);
    setForm(rule);
    setModalOpen(true);
  };

  const handleSave = async () => {
    if (!form.name?.trim()) { setFieldError("Le nom est obligatoire."); return; }
    setFieldError("");
    setSaving(true);
    try {
      const payload = { ...form };
      // Transformer la condition texte en objet JSON si nécessaire
      if (typeof payload.condition === "string") {
        try { payload.condition = JSON.parse(payload.condition); }
        catch { payload.condition = {}; }
      }
      if (editing) {
        const { data: updated } = await api.patch(ENDPOINTS.rules.update(editing.id), payload);
        setRules((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
      } else {
        const { data: created } = await api.post(ENDPOINTS.rules.create, payload);
        setRules((prev) => [...prev, created]);
      }
      setModalOpen(false);
    } finally {
      setSaving(false);
    }
  };

  const toggleEnabled = async (rule: Rule) => {
    const { data: updated } = await api.patch(ENDPOINTS.rules.update(rule.id), { enabled: !rule.enabled });
    setRules((prev) => prev.map((r) => (r.id === updated.id ? updated : r)));
  };

  const handleDelete = async (id: string) => {
    await api.delete(ENDPOINTS.rules.delete(id));
    setRules((prev) => prev.filter((r) => r.id !== id));
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-white font-medium text-lg">Règles de corrélation</h1>
        <Button size="sm" onClick={openCreate}>
          + Créer une règle
        </Button>
      </div>

      {loading && <p className="text-gray-500 text-sm">Chargement...</p>}

      <div className="flex flex-col gap-2">
        {rules.map((rule) => (
          <div
            key={rule.id}
            className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-start justify-between gap-4"
          >
            <div className="flex flex-col gap-1 min-w-0">
              <div className="flex items-center gap-2">
                <span
                  className={`w-2 h-2 rounded-full shrink-0 ${rule.enabled ? "bg-green-500" : "bg-gray-600"}`}
                />
                <p className="text-sm text-white font-medium truncate">{rule.name}</p>
                <span className="text-xs px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-400 shrink-0">
                  {rule.severity}
                </span>
              </div>
              <p className="text-xs text-gray-500 truncate pl-4">{rule.description}</p>
              {rule.condition && (
                <code className="text-xs text-cyan-400 font-mono pl-4 truncate">{JSON.stringify(rule.condition)}</code>
              )}
            </div>
            <div className="flex gap-2 shrink-0">
              <button
                onClick={() => toggleEnabled(rule)}
                className={`text-xs transition-colors ${
                  rule.enabled ? "text-green-400 hover:text-green-300" : "text-gray-500 hover:text-gray-300"
                }`}
              >
                {rule.enabled ? "Désactiver" : "Activer"}
              </button>
              <button
                onClick={() => openEdit(rule)}
                className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                Modifier
              </button>
              <button
                onClick={() => handleDelete(rule.id)}
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
        title={editing ? "Modifier la règle" : "Créer une règle"}
      >
        <div className="flex flex-col gap-4">
          <div className="space-y-1.5">
            <Label>Nom <span className="text-red-500">*</span></Label>
            <Input
              value={form.name ?? ""}
              onChange={(e) => { setForm({ ...form, name: e.target.value }); setFieldError(""); }}
              placeholder="Brute Force Detection"
            />
          </div>
          <div className="space-y-1.5">
            <Label>Description</Label>
            <Input
              value={form.description ?? ""}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Description de la règle..."
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Type de règle <span className="text-red-500">*</span></label>
              <select
                value={form.rule_type ?? "single_event"}
                onChange={(e) => setForm({ ...form, rule_type: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="single_event">Single Event</option>
                <option value="threshold">Threshold</option>
                <option value="sequence">Sequence</option>
                <option value="correlation">Correlation</option>
                <option value="ueba">UEBA</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Sévérité <span className="text-red-500">*</span></label>
              <select
                value={form.severity ?? "medium"}
                onChange={(e) => setForm({ ...form, severity: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="critical">Critique</option>
                <option value="high">Haute</option>
                <option value="medium">Moyenne</option>
                <option value="low">Basse</option>
                <option value="info">Info</option>
              </select>
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Condition (JSON) <span className="text-red-500">*</span></label>
            <p className="text-[10px] text-gray-600 mb-1">Ex: {"{\"field\": \"severity\", \"value\": \"critical\"}"}</p>
            <textarea
              rows={3}
              value={typeof form.condition === "object" ? JSON.stringify(form.condition, null, 2) : form.condition ?? ""}
              onChange={(e) => setForm({ ...form, condition: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-cyan-400 font-mono placeholder-gray-600 focus:outline-none focus:border-cyan-500 resize-none"
              placeholder='{"field": "raw_message", "value": "Failed password"}'
            />
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="enabled"
              checked={form.enabled ?? true}
              onChange={(e) => setForm({ ...form, enabled: e.target.checked })}
              className="accent-cyan-500"
            />
            <label htmlFor="enabled" className="text-sm text-gray-400">Activer la règle</label>
          </div>
          {fieldError && <p className="text-red-400 text-xs">{fieldError}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>Annuler</Button>
            <Button disabled={saving || !form.name?.trim()} onClick={handleSave}>
              {saving ? "Enregistrement..." : editing ? "Enregistrer" : "Créer"}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Rules;