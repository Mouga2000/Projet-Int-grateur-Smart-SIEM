import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ChevronLeft, ChevronRight, LogOut, Menu, UserCircle } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import ThemeSwitch from "./ThemeSwitch";
import { NAV_GROUPS } from "./Sidebar";

interface NavbarProps {
  onMenuClick: () => void;
  sidebarCollapsed: boolean;
  onSidebarCollapseChange: (collapsed: boolean) => void;
}

const Navbar = ({ onMenuClick, sidebarCollapsed, onSidebarCollapseChange }: NavbarProps) => {
  const { logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const page = useMemo(() => {
    const item = NAV_GROUPS.flatMap((group) => group.items).find((navItem) =>
      location.pathname === navItem.path || location.pathname.startsWith(`${navItem.path}/`)
    );

    if (location.pathname === "/profile") {
      return { section: "Compte", label: "Profil" };
    }

    const section = NAV_GROUPS.find((group) =>
      group.items.some((navItem) => navItem.path === item?.path)
    )?.title;

    return { section: section ?? "Console", label: item?.label ?? "Dashboard" };
  }, [location.pathname]);

  return (
    <header className="flex h-auto min-h-16 shrink-0 flex-wrap items-center gap-2 border-b bg-background px-3 py-2 sm:flex-nowrap sm:px-4">
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={onMenuClick}
        className="lg:hidden"
        aria-label="Ouvrir la navigation"
        title="Ouvrir la navigation"
      >
        <Menu className="size-4" />
      </Button>

      <Button
        variant="ghost"
        size="icon-sm"
        onClick={() => onSidebarCollapseChange(!sidebarCollapsed)}
        className="hidden lg:inline-flex"
        aria-label={sidebarCollapsed ? "Agrandir la navigation" : "Replier la navigation"}
        title={sidebarCollapsed ? "Agrandir la navigation" : "Replier la navigation"}
      >
        {sidebarCollapsed ? <ChevronRight className="size-4" /> : <ChevronLeft className="size-4" />}
      </Button>

      <div className="hidden h-4 w-px bg-border sm:block" />

      <nav className="flex min-w-0 flex-1 items-center gap-2 text-sm">
        <span className="hidden truncate text-muted-foreground sm:inline">{page.section}</span>
        <span className="hidden text-muted-foreground sm:inline">/</span>
        <span className="truncate font-medium">{page.label}</span>
      </nav>

      <div className="ml-auto flex flex-wrap items-center gap-2">
        <ThemeSwitch />
        <Button variant="ghost" size="sm" onClick={() => navigate("/profile")}>
          <UserCircle className="size-4" />
          <span className="hidden sm:inline">Profil</span>
        </Button>
        <Button variant="ghost" size="sm" onClick={logout} className="text-destructive hover:text-destructive">
          <LogOut className="size-4" />
          <span className="hidden sm:inline">Deconnexion</span>
        </Button>
      </div>
    </header>
  );
};

export default Navbar;
