import React from "react";
import { cn } from "../../lib/cn";

const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div
      className={cn(
        "rounded-xl p-8 shadow-xl border",
        "bg-card text-card-foreground border-border",
        className
      )}
    >
      {children}
    </div>
  );
};

export default Card;
