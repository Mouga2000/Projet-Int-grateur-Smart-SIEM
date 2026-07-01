// src/pages/Profile.tsx
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import authService from "@/services/authService";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ShieldCheck, ShieldOff } from "lucide-react";

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

  return (
    <div className="flex flex-col gap-6 max-w-lg">
      <h1 className="text-lg font-semibold">Profil</h1>

      <Tabs defaultValue="info">
        <TabsList>
          <TabsTrigger value="info">Informations</TabsTrigger>
          <TabsTrigger value="mfa">MFA</TabsTrigger>
        </TabsList>

        <TabsContent value="info">
          <Card>
            <CardContent className="pt-6">
              <table className="w-full text-sm">
                <tbody>
                  <tr className="border-b"><td className="py-2.5 text-muted-foreground text-xs w-32">Identifiant</td><td className="py-2.5">{user?.username}</td></tr>
                  <tr className="border-b"><td className="py-2.5 text-muted-foreground text-xs">Email</td><td className="py-2.5">{user?.email}</td></tr>
                  <tr className="border-b"><td className="py-2.5 text-muted-foreground text-xs">Rôle</td><td className="py-2.5 capitalize">{user?.role}</td></tr>
                  <tr><td className="py-2.5 text-muted-foreground text-xs">MFA</td><td className="py-2.5">
                    <Badge variant={mfaEnabled ? "default" : "outline"}>
                      {mfaEnabled ? "Activé" : "Désactivé"}
                    </Badge>
                  </td></tr>
                </tbody>
              </table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mfa">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Authentification à deux facteurs</CardTitle>
              <CardDescription>
                {mfaEnabled
                  ? "La MFA est activée sur ton compte."
                  : "Active la MFA pour sécuriser ton compte."}
              </CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              {error   && <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>}
              {success && <Alert><AlertDescription>{success}</AlertDescription></Alert>}

              {!mfaEnabled && !qrCode && (
                <Button onClick={handleMfaSetup} disabled={saving} className="self-start">
                  <ShieldCheck className="h-4 w-4 mr-2" />
                  Configurer la MFA
                </Button>
              )}

              {qrCode && (
                <div className="flex flex-col gap-4">
                  <p className="text-xs text-muted-foreground">
                    Scanne ce QR Code avec Google Authenticator ou équivalent.
                  </p>
                  <img src={`data:image/png;base64,${qrCode}`} alt="QR Code MFA" className="w-40 h-40 rounded-md border" />
                  <div className="space-y-1.5">
                    <Label>Code de vérification</Label>
                    <Input
                      maxLength={6}
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ""))}
                      placeholder="000000"
                      className="text-center tracking-widest"
                    />
                  </div>
                  <Button onClick={handleMfaVerify} disabled={mfaCode.length !== 6 || saving}>
                    Activer
                  </Button>
                </div>
              )}

              {mfaEnabled && (
                <div className="flex flex-col gap-3 pt-2 border-t">
                  <Label>Mot de passe actuel (pour désactiver)</Label>
                  <Input
                    type="password"
                    value={currentPwd}
                    onChange={(e) => setCurrentPwd(e.target.value)}
                    placeholder="••••••••"
                  />
                  <Button variant="destructive" disabled={!currentPwd || saving} onClick={handleMfaDisable} className="self-start">
                    <ShieldOff className="h-4 w-4 mr-2" />
                    Désactiver la MFA
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Profile;