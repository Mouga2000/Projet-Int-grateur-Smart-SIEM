import { useEffect } from "react";
import type { ReactNode } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES = {
  sm: "max-w-sm",
  md: "max-w-lg",
  lg: "max-w-2xl",
};

const Modal = ({ open, onClose, title, children, size = "md" }: ModalProps) => {
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 px-4 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className={`w-full ${SIZE_CLASSES[size]} rounded-xl border border-border bg-card text-card-foreground shadow-xl`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border px-6 py-4">
          <h2 className="text-sm font-medium text-foreground">{title}</h2>
          <button
            onClick={onClose}
            className="text-lg leading-none text-muted-foreground transition-colors hover:text-foreground"
          >
            ×
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
