import React from "react";
import { cn } from "../../lib/cn";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline";
};

const VARIANTS: Record<string, string> = {
  primary: "bg-primary hover:bg-primary/90 text-primary-foreground",
  ghost: "bg-transparent text-foreground hover:bg-muted",
  outline: "border border-input bg-background text-foreground hover:bg-muted",
};

const Button = ({ variant = "primary", className, children, ...props }: ButtonProps) => {
  return (
    <button
      {...props}
      className={cn(
        "inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition",
        VARIANTS[variant],
        className
      )}
    >
      {children}
    </button>
  );
};

export default Button;
