// src/pages/audit/Verify.tsx
import { useState } from "react";
import auditService from "../../services/auditService";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";

interface VerifyResult {
  valid: boolean;
  hash: string;
  computedHash: string;
}

const Verify = () => {
  const [logId, setLogId]       = useState("");
  const [result, setResult]     = useState<VerifyResult | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const handleVerify = async () => {
    if (!logId.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await auditService.verify(logId.trim());
      setResult(data);
    } catch {
      setError("Log introuvable ou erreur de vérification.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <div>
        <h1 className="text-white font-medium text-lg">Vérification d'intégrité</h1>
        <p className="text-gray-500 text-sm">
          Vérifiez la chaîne de custody d'un log archivé via son hash SHA-256.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex flex-col gap-4">
        <Input
          label="ID du log à vérifier"
          value={logId}
          onChange={(e) => setLogId(e.target.value)}
          placeholder="UUID du log..."
        />
        <Button
          variant="primary"
          disabled={!logId.trim()}
          loading={loading}
          onClick={handleVerify}
          className="self-start"
        >
          Vérifier l'intégrité
        </Button>
      </div>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      {result && (
        <div className={`bg-gray-900 border rounded-xl p-5 flex flex-col gap-4 ${
          result.valid ? "border-green-800" : "border-red-800"
        }`}>
          {/* Verdict */}
          <div className="flex items-center gap-3">
            <span className={`text-2xl ${result.valid ? "text-green-400" : "text-red-400"}`}>
              {result.valid ? "✓" : "✗"}
            </span>
            <div>
              <p className={`font-medium text-sm ${result.valid ? "text-green-400" : "text-red-400"}`}>
                {result.valid ? "Intégrité vérifiée" : "Intégrité compromise"}
              </p>
              <p className="text-xs text-gray-500">
                {result.valid
                  ? "Le hash stocké correspond au hash calculé."
                  : "Le hash stocké ne correspond pas au hash calculé. Le log a peut-être été modifié."}
              </p>
            </div>
          </div>

          {/* Hashes */}
          <div className="flex flex-col gap-2">
            <div>
              <p className="text-xs text-gray-500 mb-1">Hash stocké</p>
              <code className="block text-xs text-gray-300 font-mono bg-gray-950 border border-gray-800 rounded p-2 break-all">
                {result.hash}
              </code>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Hash calculé</p>
              <code className={`block text-xs font-mono bg-gray-950 border rounded p-2 break-all ${
                result.valid
                  ? "text-green-400 border-green-900"
                  : "text-red-400 border-red-900"
              }`}>
                {result.computedHash}
              </code>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Verify;