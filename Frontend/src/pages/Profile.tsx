// src/pages/Profile.tsx
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import authService from "@/services/authService";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ShieldCheck,
  ShieldOff,
  Loader2,
  User,
  Mail,
  Fingerprint,
  KeyRound,
} from "lucide-react";

const fieldVariants = {
  hidden: { opacity: 0, y: 8 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.05, duration: 0.25 },
  }),
};

const Profile = () => {
  const { user } = useAuth();
  const [mfaEnabled, setMfaEnabled] = useState(user?.mfa_enabled ?? false);
  const [qrCode, setQrCode]         = useState<string | null>(null);
  const [mfaCode, setMfaCode]       = useState("");
  const [currentPwd, setCurrentPwd] = useState("");
  const [saving, setSaving]         = useState(false);
  const [error, setError]           = useState<string | null>(null);
  const [success, setSuccess]       = useState<string | null>(null);

  useEffect(() => {
    authService.mfaStatus().then((data) => setMfaEnabled(data.mfa_enabled));
  }, []);

  const handleMfaSetup = async () => {
    setSaving(true); setError(null);
    try {
      const data = await authService.mfaSetup();
      setQrCode(data.qr_code);
    } catch {
      setError("Erreur lors de la configuration MFA.");
    } finally {
      setSaving(false);
    }
  };

  const handleMfaVerify = async () => {
    setSaving(true); setError(null); setSuccess(null);
    try {
      await authService.mfaVerify(mfaCode);
      setMfaEnabled(true);
      setQrCode(null);
      setMfaCode("");
      setSuccess("MFA activé avec succès.");
    } catch {
      setError("Code invalide.");
    } finally {
      setSaving(false);
    }
  };

  const handleMfaDisable = async () => {
    setSaving(true); setError(null); setSuccess(null);
    try {
      await authService.mfaDisable(currentPwd);
      setMfaEnabled(false);
      setCurrentPwd("");
      setSuccess("MFA désactivé.");
    } catch {
      setError("Mot de passe incorrect.");
    } finally {
      setSaving(false);
    }
  };

  const infoFields = [
    { icon: User, label: "Identifiant", value: user?.username },
    { icon: Mail, label: "Email", value: user?.email },
    { icon: Fingerprint, label: "Rôle", value: user?.role, capitalize: true },
  ];

  return (
    <motion.div
      className="flex flex-col gap-6 max-w-lg"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
    >
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center rounded-full bg-blue-50 p-2.5">
          <User className="h-5 w-5 text-blue-700" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-slate-900">Profil</h1>
          <p className="text-xs text-slate-500">Gère ton compte et ta sécurité</p>
        </div>
      </div>

      <Tabs defaultValue="info">
        <TabsList>
          <TabsTrigger value="info">Informations</TabsTrigger>
          <TabsTrigger value="mfa">MFA</TabsTrigger>
        </TabsList>

        <TabsContent value="info">
          <Card className="border-slate-200">
            <CardContent className="pt-6">
              <div className="flex flex-col divide-y divide-slate-100">
                {infoFields.map((f, i) => (
                  <motion.div
                    key={f.label}
                    custom={i}
                    initial="hidden"
                    animate="show"
                    variants={fieldVariants}
                    className="flex items-center gap-3 py-3"
                  >
                    <f.icon className="h-4 w-4 text-slate-400 shrink-0" />
                    <span className="text-xs text-slate-500 w-24 shrink-0">{f.label}</span>
                    <span className={cn("text-sm text-slate-900", f.capitalize && "capitalize")}>
                      {f.value ?? "—"}
                    </span>
                  </motion.div>
                ))}

                <motion.div
                  custom={infoFields.length}
                  initial="hidden"
                  animate="show"
                  variants={fieldVariants}
                  className="flex items-center gap-3 py-3"
                >
                  {mfaEnabled ? (
                    <ShieldCheck className="h-4 w-4 text-emerald-500 shrink-0" />
                  ) : (
                    <ShieldOff className="h-4 w-4 text-slate-400 shrink-0" />
                  )}
                  <span className="text-xs text-slate-500 w-24 shrink-0">MFA</span>
                  <Badge
                    variant={mfaEnabled ? "default" : "outline"}
                    className={mfaEnabled ? "bg-blue-700 hover:bg-blue-700" : ""}
                  >
                    {mfaEnabled ? "Activé" : "Désactivé"}
                  </Badge>
                </motion.div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mfa">
          <Card className="border-slate-200">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <KeyRound className="h-4 w-4 text-blue-700" />
                Authentification à deux facteurs
              </CardTitle>
              <CardDescription>
                {mfaEnabled
                  ? "La MFA est activée sur ton compte."
                  : "Active la MFA pour sécuriser ton compte."}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <AnimatePresence mode="popLayout">
                {error && (
                  <motion.div
                    key="error"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <Alert variant="destructive">
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  </motion.div>
                )}
                {success && (
                  <motion.div
                    key="success"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                  >
                    <Alert className="border-emerald-200 bg-emerald-50 text-emerald-800">
                      <AlertDescription>{success}</AlertDescription>
                    </Alert>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence mode="wait">
                {!mfaEnabled && !qrCode && (
                  <motion.div
                    key="setup"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <Button
                      onClick={handleMfaSetup}
                      disabled={saving}
                      className="self-start bg-blue-700 hover:bg-blue-800"
                    >
                      {saving
                        ? <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        : <ShieldCheck className="h-4 w-4 mr-2" />}
                      Configurer la MFA
                    </Button>
                  </motion.div>
                )}

                {qrCode && (
                  <motion.div
                    key="qr"
                    className="flex flex-col gap-4"
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    <p className="text-xs text-slate-500">
                      Scanne ce QR Code avec Google Authenticator ou équivalent.
                    </p>
                    <motion.img
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.1 }}
                      src={qrCode.startsWith("data:") ? qrCode : `data:image/png;base64,${qrCode}`}
                      alt="QR Code MFA"
                      className="w-40 h-40 rounded-md border border-slate-200"
                    />
                    <div className="space-y-1.5">
                      <Label>Code de vérification</Label>
                      <Input
                        maxLength={6}
                        value={mfaCode}
                        onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ""))}
                        placeholder="000000"
                        className="text-center tracking-[0.5em] font-mono focus-visible:ring-blue-600"
                      />
                    </div>
                    <Button
                      onClick={handleMfaVerify}
                      disabled={mfaCode.length !== 6 || saving}
                      className="bg-blue-700 hover:bg-blue-800"
                    >
                      {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      Activer
                    </Button>
                  </motion.div>
                )}

                {mfaEnabled && (
                  <motion.div
                    key="disable"
                    className="flex flex-col gap-3 pt-2 border-t border-slate-100"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                  >
                    <Label>Mot de passe actuel (pour désactiver)</Label>
                    <Input
                      type="password"
                      value={currentPwd}
                      onChange={(e) => setCurrentPwd(e.target.value)}
                      placeholder="••••••••"
                      className="focus-visible:ring-blue-600"
                    />
                    <Button
                      variant="destructive"
                      disabled={!currentPwd || saving}
                      onClick={handleMfaDisable}
                      className="self-start"
                    >
                      {saving && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      <ShieldOff className="h-4 w-4 mr-2" />
                      Désactiver la MFA
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
};

export default Profile;