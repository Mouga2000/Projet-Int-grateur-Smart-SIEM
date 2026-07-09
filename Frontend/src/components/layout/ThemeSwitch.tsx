import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/Button";

const ThemeSwitch = () => {
  const [theme, setTheme] = useState<"light" | "dark">(() => {
    try {
      return (localStorage.getItem("theme") as "light" | "dark") ?? "light";
    } catch {
      return "light";
    }
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    try {
      localStorage.setItem("theme", theme);
    } catch {
      // Ignore storage errors in private browsing contexts.
    }
  }, [theme]);

  return (
    <Button
      variant="ghost"
      size="icon-sm"
      aria-label="Changer le theme"
      title="Changer le theme"
      onClick={() => setTheme((current) => (current === "dark" ? "light" : "dark"))}
    >
      {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
    </Button>
  );
};

export default ThemeSwitch;
