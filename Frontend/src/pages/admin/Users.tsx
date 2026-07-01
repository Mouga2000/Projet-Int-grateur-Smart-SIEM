// src/pages/admin/Users.tsx
import { useEffect, useState } from "react";
import type { User } from "@/types/user";
import { Role } from "@/config/roles";
import userService from "../../services/userService";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Plus, Loader2 } from "lucide-react";

const Users = () => {
  const [users, setUsers]     = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole]         = useState<string>(Role.LECTEUR);
  const [saving, setSaving]     = useState(false);
  const [error, setError]       = useState<string | null>(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.list();
      setUsers(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async () => {
    setError(null);
    setSaving(true);
    try {
      const created = await userService.create({ username, email, password, role, perimeter: [] });
      setUsers((prev) => [...prev, created]);
      setDialogOpen(false);
      setUsername(""); setEmail(""); setPassword(""); setRole(Role.LECTEUR);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Erreur lors de la création.");
    } finally {
      setSaving(false);
    }
  };

  const handleRoleChange = async (username: string, newRole: string) => {
    const updated = await userService.updateRole(username, newRole);
    setUsers((prev) => prev.map((u) => (u.username === username ? updated : u)));
  };

  return (
    <div className="flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Gestion des utilisateurs</h1>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Créer un utilisateur
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Créer un utilisateur</DialogTitle>
            </DialogHeader>
            <div className="flex flex-col gap-4">
              <div className="space-y-1.5">
                <Label>Identifiant</Label>
                <Input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="nom.prenom" />
              </div>
              <div className="space-y-1.5">
                <Label>Email</Label>
                <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nom@domaine.com" />
              </div>
              <div className="space-y-1.5">
                <Label>Mot de passe</Label>
                <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="min. 8 caractères" />
              </div>
              <div className="space-y-1.5">
                <Label>Rôle</Label>
                <Select value={role} onValueChange={setRole}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {Object.values(Role).map((r) => (
                      <SelectItem key={r} value={r}>{r}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </div>
            <DialogFooter>
              <Button variant="ghost" onClick={() => setDialogOpen(false)}>Annuler</Button>
              <Button disabled={!username || !email || password.length < 8 || saving} onClick={handleCreate}>
                {saving ? "Création..." : "Créer"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
          <Loader2 className="h-4 w-4 animate-spin" /> Chargement...
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6">
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
                        <SelectTrigger className="w-36 h-8 text-xs">
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
                    <TableCell className="text-xs text-muted-foreground">
                      {u.last_login ? new Date(u.last_login).toLocaleString("fr-FR") : "Jamais"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Users;