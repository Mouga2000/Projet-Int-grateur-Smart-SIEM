// src/components/layout/Sidebar.tsx
import { NavLink } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Role } from "@/config/roles";
import { cn } from "../../lib/utils";
import {
  LayoutDashboard, FileSearch, ShieldAlert, Bell, Users,
  Trash2, Archive, Link2, ScrollText, Siren, Settings2, ShieldCheck,
  Radio,
} from "lucide-react";

interface NavItem {
  path: string;
  label: string;
  icon: React.ElementType;
  roles: Role[];
}

const NAV_ITEMS: NavItem[] = [
  { path: "/dashboard",       label: "Dashboard",          icon: LayoutDashboard, roles: [Role.LECTEUR, Role.ANALYSTE, Role.RSSI, Role.ADMINISTRATEUR] },
  { path: "/crisis-room",     label: "Crisis Room",        icon: Radio,           roles: [Role.ANALYSTE, Role.RSSI, Role.ADMINISTRATEUR] },
  { path: "/logs",            label: "Logs",                icon: FileSearch,      roles: [Role.LECTEUR, Role.ANALYSTE, Role.ADMINISTRATEUR] },
  { path: "/investigations",  label: "Investigations",      icon: ShieldAlert,     roles: [Role.ANALYSTE, Role.ADMINISTRATEUR] },
  { path: "/alerts",          label: "Alertes",             icon: Bell,            roles: [Role.ANALYSTE, Role.ADMINISTRATEUR, Role.LECTEUR] },
  { path: "/admin/users",     label: "Utilisateurs",        icon: Users,           roles: [Role.ADMINISTRATEUR] },
  { path: "/admin/rules",     label: "Règles",              icon: ScrollText,      roles: [Role.ADMINISTRATEUR] },
  { path: "/admin/playbooks", label: "Playbooks SOAR",      icon: Siren,           roles: [Role.ADMINISTRATEUR] },
  { path: "/admin/system",    label: "Système",             icon: Settings2,       roles: [Role.ADMINISTRATEUR] },
  { path: "/admin/purge",     label: "Rétention",           icon: Trash2,          roles: [Role.ADMINISTRATEUR] },
  { path: "/audit/logs",      label: "Logs d'audit",        icon: FileSearch,      roles: [Role.AUDITEUR, Role.ADMINISTRATEUR] },
  { path: "/audit/verify",    label: "Vérification",        icon: ShieldCheck,     roles: [Role.AUDITEUR, Role.ADMINISTRATEUR] },
  { path: "/archive",         label: "Archives",            icon: Archive,         roles: [Role.ADMINISTRATEUR] },
  { path: "/archive/chain",   label: "Chaîne d'intégrité",  icon: Link2,           roles: [Role.ADMINISTRATEUR] },
];

const Sidebar = () => {
  const { user, hasAnyRole } = useAuth();
  const visible = NAV_ITEMS.filter((item) => hasAnyRole(item.roles));

  return (
    <aside className="w-56 border-r bg-card flex flex-col">
      <div className="px-5 py-5 border-b">
        <span className="font-bold tracking-widest text-sm text-primary">SMART SIEM</span>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 px-2">
        <ul className="space-y-1">
          {visible.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  className={({ isActive }: { isActive: boolean }) =>
                    cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                      isActive
                        ? "bg-primary/10 text-primary"
                        : "text-muted-foreground hover:bg-accent hover:text-foreground"
                    )
                  }
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="px-4 py-4 border-t">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xs font-semibold">
            {user?.username?.slice(0, 2).toUpperCase() ?? "??"}
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium truncate">{user?.username}</p>
            <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;