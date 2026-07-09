// src/components/login-form.tsx
import { useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  ShieldAlert,
  ShieldCheck,
  User,
  Lock,
  Loader2,
  ArrowLeft,
} from "lucide-react";

type Step = "credentials" | "mfa";

/* ---------------------------------------------------------------------- */
/*  Panneau de droite : "écran de supervision" — radar + ticker de logs    */
/* ---------------------------------------------------------------------- */

const FAKE_LOG_LINES = [
  "10:42:07  auth.session.established  src=10.12.4.8",
  "10:42:11  rule.match  sigma:T1110  severity=medium",
  "10:42:14  net.flow.analyzed  bytes=48213",
  "10:42:19  correlation.engine  events=312 window=60s",
  "10:42:23  alert.suppressed  reason=known_pattern",
  "10:42:28  asset.heartbeat  host=fw-edge-02  ok",
];

function MonitoringPanel() {
  const prefersReducedMotion = useReducedMotion();

  const blips = [
    { top: "28%", left: "62%", delay: 0 },
    { top: "58%", left: "34%", delay: 0.6 },
    { top: "44%", left: "78%", delay: 1.1 },
    { top: "70%", left: "60%", delay: 1.6 },
  ];

  return (
    <div className="relative hidden md:flex flex-col justify-between overflow-hidden bg-[#0B1220] p-8">
      {/* grille de fond */}
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(to right, #1d4ed8 1px, transparent 1px), linear-gradient(to bottom, #1d4ed8 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* en-tête du panneau */}
      <div className="relative z-10 flex items-center gap-2 font-mono text-[11px] tracking-widest text-sky-400/80">
        <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
        SYSTEME OPERATIONNEL
      </div>

      {/* radar central */}
      <div className="relative z-10 flex flex-1 items-center justify-center">
        <div className="relative h-56 w-56">
          {/* anneaux */}
          {[1, 0.72, 0.44].map((scale, i) => (
            <span
              key={i}
              className="absolute inset-0 rounded-full border border-sky-500/25"
              style={{ transform: `scale(${scale})` }}
            />
          ))}

          {/* sweep radar */}
          {!prefersReducedMotion && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background:
                  "conic-gradient(from 0deg, rgba(56,189,248,0.35), transparent 35%)",
              }}
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
            />
          )}

          {/* blips */}
          {blips.map((b, i) => (
            <motion.span
              key={i}
              className="absolute h-1.5 w-1.5 rounded-full bg-sky-400"
              style={{ top: b.top, left: b.left }}
              animate={{ opacity: [0.2, 1, 0.2], scale: [0.8, 1.3, 0.8] }}
              transition={{
                repeat: Infinity,
                duration: 2.2,
                delay: b.delay,
                ease: "easeInOut",
              }}
            />
          ))}

          {/* coeur : shield */}
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div
              className="flex items-center justify-center rounded-full bg-blue-600/10 p-5 ring-1 ring-blue-500/30"
              animate={
                prefersReducedMotion
                  ? {}
                  : { boxShadow: [
                      "0 0 0 0 rgba(56,189,248,0.35)",
                      "0 0 0 14px rgba(56,189,248,0)",
                    ] }
              }
              transition={{ repeat: Infinity, duration: 2.2 }}
            >
              <ShieldCheck className="h-10 w-10 text-sky-400" />
            </motion.div>
          </div>
        </div>
      </div>

      {/* wordmark */}
      <div className="relative z-10 text-center">
        <h2 className="font-mono text-xl font-bold tracking-tight text-white">
          SMART&nbsp;SIEM
        </h2>
        <p className="mt-1 text-xs text-slate-400">
          Détection, corrélation et réponse aux incidents en temps réel.
        </p>
        <div className="mt-4 flex justify-center gap-2 text-[10px] font-mono text-sky-400/70">
          <span className="rounded border border-sky-500/25 px-2 py-1">SIEM</span>
          <span className="rounded border border-sky-500/25 px-2 py-1">SOAR</span>
          <span className="rounded border border-sky-500/25 px-2 py-1">MFA</span>
        </div>
      </div>

      {/* ticker de logs */}
      <div className="relative z-10 mt-6 h-16 overflow-hidden rounded-md border border-white/5 bg-black/30">
        <motion.div
          className="flex flex-col gap-1 p-2 font-mono text-[10px] leading-tight text-sky-300/50"
          animate={prefersReducedMotion ? {} : { y: ["0%", "-50%"] }}
          transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
        >
          {[...FAKE_LOG_LINES, ...FAKE_LOG_LINES].map((line, i) => (
            <span key={i} className="whitespace-nowrap">
              {line}
            </span>
          ))}
        </motion.div>
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------- */
/*  Formulaire                                                             */
/* ---------------------------------------------------------------------- */

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


  const usernameRef = useRef<HTMLInputElement>(null);
  const passwordRef = useRef<HTMLInputElement>(null);

  const from = (location.state as any)?.from?.pathname ?? null;

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    // Lecture via FormData : capte l'autofill même sans onChange
    const form = e.currentTarget as HTMLFormElement;
    const data = new FormData(form);
    const liveUsername = (data.get("username") as string) || usernameRef.current?.value || username;
    const livePassword = (data.get("password") as string) || passwordRef.current?.value || password;
    try {
      await login(liveUsername, livePassword);
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
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.45, ease: "easeOut" }}
      >
        <Card className="overflow-hidden p-0 border-slate-200 shadow-sm">
          <CardContent className="grid p-0 md:grid-cols-2">
            {/* Formulaire */}
            <div className="p-6 md:p-8 bg-white">
              <div className="flex flex-col gap-6">
                {/* Header */}
                <div className="flex flex-col items-center text-center gap-1">
                  <div className="mb-1 flex items-center justify-center rounded-full p-2 overflow-hidden bg-transparent dark:bg-blue-50">
                    <img src="/logo.png" alt="Smart SIEM" className="h-10 w-10 rounded-full object-contain" />
                  </div>
                  <h1 className="text-2xl font-bold text-slate-900">
                    {step === "credentials" ? "Connexion" : "Vérification MFA"}
                  </h1>
                  <p className="text-sm text-slate-500 text-balance">
                    {step === "credentials"
                      ? "Connectez-vous à votre espace SMART SIEM"
                      : "Saisissez le code généré par votre application"}
                  </p>
                </div>

                <AnimatePresence mode="wait">
                  {step === "credentials" && (
                    <motion.form
                      key="credentials"
                      onSubmit={handleLogin}
                      className="flex flex-col gap-4"
                      initial={{ opacity: 0, x: -16 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 16 }}
                      transition={{ duration: 0.25 }}
                    >
                      <div className="grid gap-2">
                        <Label htmlFor="username">Identifiant</Label>
                        <div className="relative">
                          <User className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                          <Input
                            id="username"
                            name="username"
                            autoComplete="username"
                            required
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="nom.prenom"
                            className="pl-9 focus-visible:ring-blue-600"
                          />
                        </div>
                      </div>
                      <div className="grid gap-2">
                        <Label htmlFor="password">Mot de passe</Label>
                        <div className="relative">
                          <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                          <Input
                            id="password"
                            name="password"
                            type="password"
                            autoComplete="current-password"
                            required
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            className="pl-9 focus-visible:ring-blue-600"
                          />
                        </div>
                      </div>

                      <AnimatePresence>
                        {error && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                          >
                            <Alert variant="destructive">
                              <ShieldAlert className="h-4 w-4" />
                              <AlertDescription>{error}</AlertDescription>
                            </Alert>
                          </motion.div>
                        )}
                      </AnimatePresence>

                      <Button
                        type="submit"
                        className="w-full bg-blue-700 hover:bg-blue-800"
                        disabled={loading}
                      >
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {loading ? "Connexion..." : "Se connecter"}
                      </Button>
                    </motion.form>
                  )}

                  {step === "mfa" && (
                    <motion.form
                      key="mfa"
                      onSubmit={handleMfaSubmit}
                      className="flex flex-col gap-4"
                      initial={{ opacity: 0, x: 16 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -16 }}
                      transition={{ duration: 0.25 }}
                    >
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
                          className="text-center tracking-[0.5em] text-lg font-mono focus-visible:ring-blue-600"
                        />
                      </div>

                      <AnimatePresence>
                        {error && (
                          <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                          >
                            <Alert variant="destructive">
                              <ShieldAlert className="h-4 w-4" />
                              <AlertDescription>{error}</AlertDescription>
                            </Alert>
                          </motion.div>
                        )}
                      </AnimatePresence>

                      <Button
                        type="submit"
                        className="w-full bg-blue-700 hover:bg-blue-800"
                        disabled={loading || mfaCode.length !== 6}
                      >
                        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        {loading ? "Vérification..." : "Vérifier"}
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        className="w-full text-slate-500"
                        onClick={() => { setStep("credentials"); setError(null); setMfaCode(""); }}
                      >
                        <ArrowLeft className="mr-2 h-4 w-4" />
                        Retour
                      </Button>
                    </motion.form>
                  )}
                </AnimatePresence>
              </div>
            </div>

            {/* Panel droit — supervision temps réel */}
            <MonitoringPanel />
          </CardContent>
        </Card>
      </motion.div>

      <p className="text-slate-400 text-center text-xs text-balance">
        Accès réservé au personnel autorisé. Toute tentative non autorisée est journalisée.
      </p>
    </div>
  );
}