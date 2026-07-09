import React from "react";
import { cn } from "../../lib/cn";

type Props = React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string };

const Select = ({ label, className, children, ...props }: Props) => {
  return (
    <div>
      {label && <label className="mb-1 block text-sm text-muted-foreground">{label}</label>}
      <select
        {...props}
        className={cn(
          "w-full rounded-md border px-3 py-2 text-sm transition-colors outline-none",
          "border-input bg-background text-foreground",
          "focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50",
          className
        )}
      >
        {children}
      </select>
    </div>
  );
};

export default Select;
