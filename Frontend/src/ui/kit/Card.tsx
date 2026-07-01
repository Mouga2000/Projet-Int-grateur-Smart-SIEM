import React from "react";
import { cn } from "../../lib/cn";

const Card = ({ children, className }: { children: React.ReactNode; className?: string }) => {
  return (
    <div
      className={cn(
        "rounded-xl p-8 shadow-xl",
        "bg-gray-900 border border-gray-800 text-white",
        "dark:bg-white dark:text-gray-900 dark:border-gray-200",
        className
      )}
    >
      {children}
    </div>
  );
};

export default Card;
