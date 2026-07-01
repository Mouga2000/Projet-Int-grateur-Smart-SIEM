// src/components/login-form.tsx
import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ShieldAlert, ShieldCheck } from "lucide-react";

type Step = "credentials" | "mfa";

export function LoginForm({ className, ...props }: React.ComponentProps<"div">) {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, redirectPath } = useAuth();

  const [step, setStep]         = useState<Step>("credentials");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mfaCode, setMfaCode]   = useState("");
  const [error, setError]       = useState<string | null>(null);
  const [loading, setLoading]   = useState(false);

  const from = (location.state as any)?.from?.pathname ?? null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password);
      navigate(from ?? redirectPath(), { replace: true });
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? "";
      if (detail.includes("MFA requis")) {
        setStep("mfa");
      } else {
        setError(detail || "Identifiants incorrects.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleMfaSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(username, password, mfaCode);
      navigate(from ?? redirectPath(), { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Code MFA invalide.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card className="overflow-hidden p-0">
        <CardContent className="grid p-0 md:grid-cols-2">
          {/* Formulaire */}
          <div className="p-6 md:p-8">
            <div className="flex flex-col gap-6">
              {/* Header */}
              <div className="flex flex-col items-center text-center">
                <h1 className="text-2xl font-bold">
                  {step === "credentials" ? "Connexion" : "Vérification MFA"}
                </h1>
                <p className="text-muted-foreground text-balance">
                  {step === "credentials"
                    ? "Connectez-vous à votre espace SMART SIEM"
                    : "Saisissez le code généré par votre application"}
                </p>
              </div>

              {/* Credentials step */}
              {step === "credentials" && (
                <form onSubmit={handleLogin} className="flex flex-col gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="username">Identifiant</Label>
                    <Input
                      id="username"
                      autoComplete="username"
                      required
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="nom.prenom"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="password">Mot de passe</Label>
                    <Input
                      id="password"
                      type="password"
                      autoComplete="current-password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                  </div>

                  {error && (
                    <Alert variant="destructive">
                      <ShieldAlert className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? "Connexion..." : "Se connecter"}
                  </Button>
                </form>
              )}

              {/* MFA step */}
              {step === "mfa" && (
                <form onSubmit={handleMfaSubmit} className="flex flex-col gap-4">
                  <div className="grid gap-2">
                    <Label htmlFor="mfa">Code de vérification</Label>
                    <Input
                      id="mfa"
                      inputMode="numeric"
                      maxLength={6}
                      autoFocus
                      required
                      value={mfaCode}
                      onChange={(e) => setMfaCode(e.target.value.replace(/\D/g, ""))}
                      placeholder="000000"
                      className="text-center tracking-widest text-lg"
                    />
                  </div>

                  {error && (
                    <Alert variant="destructive">
                      <ShieldAlert className="h-4 w-4" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  )}

                  <Button
                    type="submit"
                    className="w-full"
                    disabled={loading || mfaCode.length !== 6}
                  >
                    {loading ? "Vérification..." : "Vérifier"}
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    className="w-full"
                    onClick={() => { setStep("credentials"); setError(null); setMfaCode(""); }}
                  >
                    ← Retour
                  </Button>
                </form>
              )}
            </div>
          </div>

          {/* Panel droit — branding */}
          <div className="bg-muted relative hidden md:block">
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-8 text-center">
              <div className="flex items-center justify-center rounded-full bg-primary/10 p-6">
                <ShieldCheck className="h-16 w-16 text-primary" />
              </div>
              <h2 className="text-2xl font-bold tracking-tight">SMART SIEM</h2>
              <p className="text-muted-foreground text-sm text-balance">
                Plateforme de supervision de sécurité intelligente.<br />
                Détection, corrélation et réponse aux incidents en temps réel.
              </p>
              <div className="mt-4 flex gap-2 text-xs text-muted-foreground">
                <span className="rounded-full bg-primary/10 px-3 py-1">SIEM</span>
                <span className="rounded-full bg-primary/10 px-3 py-1">SOAR</span>
                <span className="rounded-full bg-primary/10 px-3 py-1">MFA</span>
              </div>
            </div>
          </div>

        </CardContent>
      </Card>

      <p className="text-muted-foreground text-center text-xs text-balance">
        Accès réservé au personnel autorisé. Toute tentative non autorisée est journalisée.
      </p>
    </div>
  );
}