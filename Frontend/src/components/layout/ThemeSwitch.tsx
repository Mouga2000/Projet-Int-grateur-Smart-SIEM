import { useEffect, useState } from "react";
import { IconSun, IconMoon } from "../../ui/icons";

const ThemeSwitch = () => {
  const [theme, setTheme] = useState<'light'|'dark'>(() => {
    try {
      return (localStorage.getItem('theme') as 'light'|'dark') ?? 'dark';
    } catch {
      return 'dark';
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    try { localStorage.setItem('theme', theme); } catch {}
  }, [theme]);

  return (
    <button
      aria-label="Toggle theme"
      title="Toggle theme"
      onClick={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}
      className="inline-flex items-center justify-center w-9 h-9 rounded-md bg-gray-800 dark:bg-gray-200 text-gray-200 dark:text-gray-800 hover:opacity-90 transition-colors"
    >
      {theme === 'dark' ? <IconSun className="w-4 h-4" /> : <IconMoon className="w-4 h-4" />}
    </button>
  );
};

export default ThemeSwitch;
