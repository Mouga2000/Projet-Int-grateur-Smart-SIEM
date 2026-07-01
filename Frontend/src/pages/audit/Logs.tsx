// src/pages/audit/Logs.tsx
import { useEffect, useState } from "react";
import auditService from "../../services/auditService";
import Button from "../../components/ui/Button";

interface AuditLog {
  id: string;
  userId: string;
  username: string;
  action: string;
  resource: string;
  resourceId?: string;
  ip: string;
  timestamp: string;
}

const Logs = () => {
  const [logs, setLogs]       = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal]     = useState(0);
  const [page, setPage]       = useState(1);
  const [from, setFrom]       = useState("");
  const [to, setTo]           = useState("");
  const [userId, setUserId]   = useState("");
  const [exporting, setExporting] = useState(false);
  const pageSize = 25;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await auditService.getLogs({
        from: from || undefined,
        to: to || undefined,
        userId: userId || undefined,
        page,
        size: pageSize,
      });
      setLogs(data.items);
      setTotal(data.total);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page]);

  const handleExport = async () => {
    setExporting(true);
    try {
      const blob = await auditService.export({ from: from || undefined, to: to || undefined });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement("a");
      a.href     = url;
      a.download = `audit-logs-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white font-medium text-lg">Logs d'audit</h1>
          <p className="text-gray-500 text-sm">{total} entrées</p>
        </div>
        <Button variant="secondary" size="sm" loading={exporting} onClick={handleExport}>
          Exporter CSV
        </Button>
      </div>

      {/* Filtres */}
      <div className="flex flex-wrap gap-3 bg-gray-900 border border-gray-800 rounded-xl p-4">
        <input
          type="text"
          placeholder="ID utilisateur..."
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300 placeholder-gray-600 focus:outline-none focus:border-cyan-500"
        />
        <input
          type="datetime-local"
          value={from}
          onChange={(e) => setFrom(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
        />
        <input
          type="datetime-local"
          value={to}
          onChange={(e) => setTo(e.target.value)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-gray-300 focus:outline-none focus:border-cyan-500"
        />
        <Button variant="secondary" size="sm" onClick={() => { setPage(1); fetchLogs(); }}>
          Filtrer
        </Button>
      </div>

      {loading && <p className="text-gray-500 text-sm">Chargement...</p>}

      <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="px-4 py-3 text-gray-500 font-medium text-left">Date</th>
              <th className="px-4 py-3 text-gray-500 font-medium text-left">Utilisateur</th>
              <th className="px-4 py-3 text-gray-500 font-medium text-left">Action</th>
              <th className="px-4 py-3 text-gray-500 font-medium text-left">Ressource</th>
              <th className="px-4 py-3 text-gray-500 font-medium text-left">IP</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-gray-800 last:border-0 hover:bg-gray-800/30">
                <td className="px-4 py-2.5 text-gray-500 font-mono whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleString("fr-FR")}
                </td>
                <td className="px-4 py-2.5 text-gray-300">{log.username}</td>
                <td className="px-4 py-2.5">
                  <span className="px-1.5 py-0.5 bg-gray-800 border border-gray-700 rounded text-gray-400">
                    {log.action}
                  </span>
                </td>
                <td className="px-4 py-2.5 text-gray-400">
                  {log.resource}
                  {log.resourceId && <span className="text-gray-600 font-mono"> #{log.resourceId.slice(0, 8)}</span>}
                </td>
                <td className="px-4 py-2.5 text-gray-500 font-mono">{log.ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {total > pageSize && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500">Page {page} / {Math.ceil(total / pageSize)}</span>
          <div className="flex gap-2">
            <button
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-gray-300 disabled:opacity-40"
            >
              ←
            </button>
            <button
              disabled={page >= Math.ceil(total / pageSize)}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1 bg-gray-800 border border-gray-700 rounded text-gray-300 disabled:opacity-40"
            >
              →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Logs;