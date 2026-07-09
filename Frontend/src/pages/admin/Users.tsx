import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { User } from "@/types/user";
import { Role } from "@/config/roles";
import userService from "../../services/userService";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Loader2, Users as UsersIcon } from "lucide-react";

const fadeUp = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };
const staggerContainer = { hidden: {}, show: { transition: { staggerChildren: 0.05 } } };

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<string>(Role.LECTEUR);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      setUsers(await userService.list());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); // eslint-disable-line react-hooks/set-state-in-effect
  }, []);

  const handleCreate = async () => {
    setError(null);
    setSaving(true);
    try {
      const created = await userService.create({ username, email, password, role, perimeter: [] });
      setUsers((prev) => [...prev, created]);
      setDialogOpen(false);
      setUsername("");
      setEmail("");
      setPassword("");
      setRole(Role.LECTEUR);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr?.response?.data?.detail ?? "Erreur lors de la création.");
    } finally {
      setSaving(false);
    }
  };

  const handleRoleChange = async (userName: string, newRole: string) => {
    const updated = await userService.updateRole(userName, newRole);
    setUsers((prev) => prev.map((u) => (u.username === userName ? updated : u)));
  };

  return (
    <motion.div variants={staggerContainer} initial="hidden" animate="show" className="flex flex-col gap-5">
      <motion.div variants={fadeUp} transition={{ duration: 0.3, ease: "easeOut" }} className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h1 className="text-lg font-semibold">Gestion des utilisateurs</h1>
          <AnimatePresence mode="wait">
            {!loading && (
              <motion.p
                key={users.length}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.2 }}
                className="mt-0.5 text-xs text-muted-foreground"
              >
                {users.length} utilisateur{users.length > 1 ? "s" : ""}
              </motion.p>
            )}
          </AnimatePresence>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm" className="shrink-0 self-start sm:self-auto">
              <Plus className="mr-2 h-4 w-4" />
              Créer un utilisateur
            </Button>
          </DialogTrigger>
          <DialogContent className="w-[calc(100vw-1.5rem)] max-w-lg sm:w-full">
            <DialogHeader>
              <DialogTitle>Créer un utilisateur</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-4">
              <div className="space-y-1.5">
                <Label>Identifiant <span className="text-destructive">*</span></Label>
                <Input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="nom.prenom" />
              </div>
              <div className="space-y-1.5">
                <Label>Email <span className="text-destructive">*</span></Label>
                <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nom@domaine.com" />
              </div>
              <div className="space-y-1.5">
                <Label>Mot de passe <span className="text-destructive">*</span></Label>
                <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="min. 8 caractères" />
                <AnimatePresence>
                  {password.length > 0 && password.length < 8 && (
                    <motion.p
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.15 }}
                      className="text-xs text-destructive"
                    >
                      Minimum 8 caractères
                    </motion.p>
                  )}
                </AnimatePresence>
              </div>
              <div className="space-y-1.5">
                <Label>Rôle <span className="text-destructive">*</span></Label>
                <Select value={role} onValueChange={setRole}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.values(Role).map((r) => (
                      <SelectItem key={r} value={r}>{r}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <AnimatePresence>
                {error && (
                  <motion.p
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.15 }}
                    className="text-sm text-destructive"
                  >
                    {error}
                  </motion.p>
                )}
              </AnimatePresence>
            </div>
            <DialogFooter className="gap-2 sm:gap-0">
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button disabled={!username || !email || password.length < 8 || saving} onClick={handleCreate}>
                {saving ? "Création..." : "Créer"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </motion.div>

      <AnimatePresence mode="wait">
        {loading ? (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="flex items-center justify-center gap-2 py-12 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
          </motion.div>
        ) : users.length === 0 ? (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="flex flex-col items-center gap-2 py-12 text-center">
            <UsersIcon className="h-8 w-8 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">Aucun utilisateur.</p>
          </motion.div>
        ) : (
          <motion.div key="table" variants={fadeUp} initial="hidden" animate="show" transition={{ duration: 0.3, ease: "easeOut" }}>
            <Card>
              <CardContent className="overflow-x-auto pt-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Identifiant</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Rôle</TableHead>
                      <TableHead>MFA</TableHead>
                      <TableHead>Dernière connexion</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                      {users.map((u) => (
                        <TableRow key={u.id}>
                          <TableCell className="font-medium">{u.username}</TableCell>
                          <TableCell className="text-xs text-muted-foreground">{u.email}</TableCell>
                          <TableCell>
                            <Select value={u.role} onValueChange={(v) => handleRoleChange(u.username, v)}>
                              <SelectTrigger className="h-8 w-full text-xs mx-auto max-w-[130px]">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                {Object.values(Role).map((r) => (
                                  <SelectItem key={r} value={r}>{r}</SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </TableCell>
                          <TableCell>
                            <Badge variant={u.mfa_enabled ? "default" : "outline"}>
                              {u.mfa_enabled ? "Activé" : "Désactivé"}
                            </Badge>
                          </TableCell>
                          <TableCell className="whitespace-nowrap text-xs text-muted-foreground">
                            {u.last_login ? new Date(u.last_login).toLocaleString("fr-FR") : "Jamais"}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
