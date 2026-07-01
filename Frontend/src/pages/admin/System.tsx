// src/pages/admin/System.tsx
import { useEffect, useState } from "react";
import adminService from "../../services/adminService";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

interface SystemConfig {
  retentionDays: number;
  autoPurgEnabled: boolean;
  notificationEmail: string;
  notificationSlack: string;
  maxLogSizeMb: number;
}

const System = () => {
  const [config, setConfig]   = useState<SystemConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving]   = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    adminService.getSystemConfig()
      .then(setConfig)
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    setSuccess(false);
    try {
      await adminService.updateSystemConfig(config);
      setSuccess(true);
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) return <p className="text-gray-500 text-sm">Chargement...</p>;

  return (
    <div className="flex flex-col gap-6 max-w-xl">
      <h1 className="text-white font-medium text-lg">Administration système</h1>

      {/* Rétention */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4">
        <h2 className="text-sm font-medium text-gray-300">Rétention des données</h2>
        <Input
          label="Durée de rétention (jours)"
          type="number"
          value={config.retentionDays}
          onChange={(e) => setConfig({ ...config, retentionDays: parseInt(e.target.value) })}
        />
        <Input
          label="Taille max des logs (Mo)"
          type="number"
          value={config.maxLogSizeMb}
          onChange={(e) => setConfig({ ...config, maxLogSizeMb: parseInt(e.target.value) })}
        />
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="autoPurge"
            checked={config.autoPurgEnabled}
            onChange={(e) => setConfig({ ...config, autoPurgEnabled: e.target.checked })}
            className="accent-cyan-500"
          />
          <label htmlFor="autoPurge" className="text-sm text-gray-400">
            Activer la purge automatique
          </label>
        </div>
      </div>

      {/* Notifications */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4">
        <h2 className="text-sm font-medium text-gray-300">Notifications</h2>
        <Input
          label="Email de notification"
          type="email"
          value={config.notificationEmail}
          onChange={(e) => setConfig({ ...config, notificationEmail: e.target.value })}
          placeholder="soc@domaine.com"
        />
        <Input
          label="Webhook Slack"
          value={config.notificationSlack}
          onChange={(e) => setConfig({ ...config, notificationSlack: e.target.value })}
          placeholder="https://hooks.slack.com/..."
        />
      </div>

      {success && <p className="text-green-400 text-xs">Configuration enregistrée.</p>}

      <Button variant="primary" loading={saving} onClick={handleSave} className="self-start">
        Enregistrer la configuration
      </Button>
    </div>
  );
};

export default System;