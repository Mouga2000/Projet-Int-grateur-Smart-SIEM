import React from "react";
import { cn } from "../../lib/cn";

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string | null;
};

const Input = ({ label, error, className, ...props }: Props) => {
  return (
    <div>
      {label && <label className="mb-1 block text-sm text-muted-foreground">{label}</label>}
      <input
        {...props}
        className={cn(
          "w-full rounded-md border px-3 py-2 text-sm transition-colors outline-none",
          "border-input bg-background text-foreground placeholder:text-muted-foreground",
          "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
      />
      {error && <p className="mt-1 text-xs text-destructive">{error}</p>}
    </div>
  );
};

export default Input;
