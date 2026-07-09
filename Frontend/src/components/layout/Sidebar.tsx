import { useEffect, useState, type ElementType } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { motion } from "motion/react";
import { useAuth } from "@/hooks/useAuth";
import { Role } from "@/config/roles";
import {
  Archive,
  Bell,
  FileSearch,
  Link2,
  LayoutDashboard,
  Radio,
  ScrollText,
  Settings2,
  ShieldAlert,
  ShieldCheck,
  ShieldHalf,
  Siren,
  Trash2,
  Users,
} from "lucide-react";

interface NavItem {
  path: string;
  label: string;
  icon: ElementType;
  roles: Role[];
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

interface SidebarProps {
  collapsed: boolean;
  mobileOpen: boolean;
  onCollapseChange: (collapsed: boolean) => void;
  onMobileOpenChange: (open: boolean) => void;
}

export const NAV_GROUPS: NavGroup[] = [
  {
    title: "Operations",
    items: [
      { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard, roles: [Role.LECTEUR, Role.ANALYSTE, Role.RSSI, Role.ADMINISTRATEUR] },
      { path: "/crisis-room", label: "Crisis Room", icon: Radio, roles: [Role.ANALYSTE, Role.RSSI, Role.ADMINISTRATEUR] },
      { path: "/logs", label: "Logs", icon: FileSearch, roles: [Role.LECTEUR, Role.ANALYSTE, Role.ADMINISTRATEUR] },
      { path: "/alerts", label: "Alertes", icon: Bell, roles: [Role.ANALYSTE, Role.ADMINISTRATEUR, Role.LECTEUR] },
      { path: "/investigations", label: "Investigations", icon: ShieldAlert, roles: [Role.ANALYSTE, Role.ADMINISTRATEUR] },
    ],
  },
  {
    title: "Administration",
    items: [
      { path: "/admin/users", label: "Utilisateurs", icon: Users, roles: [Role.ADMINISTRATEUR] },
      { path: "/admin/rules", label: "Regles", icon: ScrollText, roles: [Role.ADMINISTRATEUR] },
      { path: "/admin/playbooks", label: "Playbooks SOAR", icon: Siren, roles: [Role.ADMINISTRATEUR] },
      { path: "/admin/system", label: "Systeme", icon: Settings2, roles: [Role.ADMINISTRATEUR] },
      { path: "/admin/purge", label: "Retention", icon: Trash2, roles: [Role.ADMINISTRATEUR] },
    ],
  },
  {
    title: "Conformite",
    items: [
      { path: "/audit/logs", label: "Logs d'audit", icon: FileSearch, roles: [Role.AUDITEUR, Role.ADMINISTRATEUR] },
      { path: "/audit/verify", label: "Verification", icon: ShieldCheck, roles: [Role.AUDITEUR, Role.ADMINISTRATEUR] },
      { path: "/archive", label: "Archives", icon: Archive, roles: [Role.ADMINISTRATEUR] },
      { path: "/archive/chain", label: "Chaine d'integrite", icon: Link2, roles: [Role.ADMINISTRATEUR] },
    ],
  },
];

// ─── Motion presets ──────────────────────────────────────────────────────────

const overlayVariants = {
  hidden: { opacity: 0 },
  show: { opacity: 1 },
};

const asideVariants = {
  closed: { x: "-100%" },
  open: { x: 0 },
};

const groupStagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.05, delayChildren: 0.05 } },
};

const itemFade = {
  hidden: { opacity: 0, x: -6 },
  show: { opacity: 1, x: 0 },
};

const labelVariants = {
  collapsed: { opacity: 0, width: 0, marginLeft: 0 },
  expanded: { opacity: 1, width: "auto", marginLeft: 8 },
};

// lg breakpoint (Tailwind default: 1024px) — le slide mobile ne doit
// s'appliquer qu'en dessous, sinon le transform inline de motion
// écrase le "lg:static lg:translate-x-0" et cache la sidebar en desktop.
function useIsDesktop() {
  const [isDesktop, setIsDesktop] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(min-width: 1024px)").matches
  );

  useEffect(() => {
    const mql = window.matchMedia("(min-width: 1024px)");
    const handler = (e: MediaQueryListEvent) => setIsDesktop(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, []);

  return isDesktop;
}

const Sidebar = ({
  collapsed,
  mobileOpen,
  onCollapseChange,
  onMobileOpenChange,
}: SidebarProps) => {
  const { user, hasAnyRole } = useAuth();
  const location = useLocation();
  const isDesktop = useIsDesktop();
  const groups = NAV_GROUPS.map((group) => ({
    ...group,
    items: group.items.filter((item) => hasAnyRole(item.roles)),
  })).filter((group) => group.items.length > 0);

  return (
    <>
      <motion.div
        className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
        variants={overlayVariants}
        initial="hidden"
        animate={mobileOpen ? "show" : "hidden"}
        transition={{ duration: 0.2 }}
        style={{ pointerEvents: mobileOpen ? "auto" : "none" }}
        onClick={() => onMobileOpenChange(false)}
      />

      <motion.aside
        className="fixed inset-y-0 left-0 z-50 flex w-72 max-w-[85vw] flex-col overflow-hidden border-r border-sidebar-border bg-sidebar text-sidebar-foreground lg:static lg:z-auto lg:w-auto lg:max-w-none"
        variants={asideVariants}
        animate={isDesktop ? "open" : mobileOpen ? "open" : "closed"}
        initial={false}
        transition={{ duration: 0.25, ease: "easeOut" }}
      >
        <motion.div
          className="flex h-full flex-col"
          animate={{ width: isDesktop ? (collapsed ? 64 : 256) : "100%" }}
          initial={false}
          transition={{ duration: 0.25, ease: "easeOut" }}
        >
          <div className="flex h-16 shrink-0 items-center gap-2 border-b border-sidebar-border px-3">
            <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <ShieldHalf className="size-4" />
            </div>
            <motion.div
              className="min-w-0 overflow-hidden"
              variants={labelVariants}
              animate={collapsed ? "collapsed" : "expanded"}
              initial={false}
              transition={{ duration: 0.2, ease: "easeOut" }}
            >
              <p className="truncate text-sm font-semibold">Smart SIEM</p>
              <p className="truncate text-xs text-sidebar-foreground/60">Security console</p>
            </motion.div>
          </div>

          <nav className="flex-1 overflow-y-auto px-2 py-3">
            {groups.map((group) => (
              <div key={group.title} className="mb-4">
                <motion.p
                  className="mb-1 overflow-hidden whitespace-nowrap px-2 text-[0.68rem] font-medium uppercase tracking-wide text-sidebar-foreground/50"
                  animate={{ opacity: collapsed ? 0 : 1, height: collapsed ? 0 : "auto" }}
                  initial={false}
                  transition={{ duration: 0.2 }}
                >
                  {group.title}
                </motion.p>
                <motion.ul
                  className="space-y-1"
                  variants={groupStagger}
                  initial="hidden"
                  animate="show"
                >
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname.startsWith(item.path);
                    return (
                      <motion.li key={item.path} variants={itemFade}>
                        <NavLink
                          to={item.path}
                          title={collapsed ? item.label : undefined}
                          onClick={() => onMobileOpenChange(false)}
                           className="relative flex h-10 items-center rounded-md px-2 text-sm font-medium text-sidebar-foreground/75 sm:h-9"
                        >
                          {isActive && (
                            <motion.span
                              layoutId="sidebar-active-pill"
                              className="absolute inset-0 rounded-md bg-sidebar-accent shadow-sm"
                              transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                            />
                          )}
                          <motion.span
                            className="relative z-10 flex items-center"
                            animate={{ color: isActive ? "var(--sidebar-accent-foreground)" : undefined }}
                            initial={false}
                          >
                            <Icon className="size-4 shrink-0" />
                            <motion.span
                              className="truncate overflow-hidden whitespace-nowrap"
                              variants={labelVariants}
                              animate={collapsed ? "collapsed" : "expanded"}
                              initial={false}
                              transition={{ duration: 0.2, ease: "easeOut" }}
                            >
                              {item.label}
                            </motion.span>
                          </motion.span>
                        </NavLink>
                      </motion.li>
                    );
                  })}
                </motion.ul>
              </div>
            ))}
          </nav>

          <div className="shrink-0 border-t border-sidebar-border p-3">
            <div className="flex items-center">
              <motion.div
                className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-sidebar-accent text-xs font-semibold text-sidebar-accent-foreground"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.15 }}
              >
                {user?.username?.slice(0, 2).toUpperCase() ?? "??"}
              </motion.div>
              <motion.div
                className="min-w-0 overflow-hidden"
                variants={labelVariants}
                animate={collapsed ? "collapsed" : "expanded"}
                initial={false}
                transition={{ duration: 0.2, ease: "easeOut" }}
              >
                <p className="truncate text-xs font-medium">{user?.username}</p>
                <p className="truncate text-xs capitalize text-muted-foreground">{user?.role}</p>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
