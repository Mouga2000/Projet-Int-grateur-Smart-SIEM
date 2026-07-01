// src/components/layout/Navbar.tsx
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/Button";
import { LogOut, UserCircle } from "lucide-react";

const Navbar = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="h-14 border-b bg-card flex items-center justify-end px-6 gap-2">
      <Button variant="ghost" size="sm" onClick={() => navigate("/profile")}>
        <UserCircle className="h-4 w-4 mr-2" />
        Profil
      </Button>
      <Button variant="ghost" size="sm" onClick={logout} className="text-destructive hover:text-destructive">
        <LogOut className="h-4 w-4 mr-2" />
        Déconnexion
      </Button>
    </header>
  );
};

export default Navbar;