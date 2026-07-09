import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Initialize theme early to avoid flash
try {
  const theme = localStorage.getItem("theme") ?? "light";
  document.documentElement.classList.toggle("dark", theme === "dark");
} catch {}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
