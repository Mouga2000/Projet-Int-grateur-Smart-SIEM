import React from "react";
import { cn } from "../../lib/cn";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline";
};

const VARIANTS: Record<string, string> = {
  primary: "bg-cyan-600 hover:bg-cyan-500 text-white",
  ghost: "bg-transparent text-gray-200 hover:bg-gray-800",
  outline: "border border-gray-700 text-gray-200",
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
