import React from "react";
import { cn } from "../../lib/cn";

type Props = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string | null;
};

const Input = ({ label, error, className, ...props }: Props) => {
  return (
    <div>
      {label && <label className="block text-sm text-gray-300 mb-1">{label}</label>}
      <input
        {...props}
        className={cn(
          "w-full rounded-md px-3 py-2 text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500",
          "bg-gray-800 text-white border border-gray-700",
          "dark:bg-white dark:text-gray-900 dark:border-gray-200",
          className
        )}
      />
      {error && <p className="text-xs text-red-400 mt-1">{error}</p>}
    </div>
  );
};

export default Input;
