// src/components/logs/SeverityBadge.tsx
import { Badge } from "@/components/ui/badge";
import type { Severity } from "../../types/log";
import { cn } from "../../lib/utils";

const SEVERITY_STYLES: Record<Severity, string> = {
  critical: "bg-red-500/15 text-red-600 border-red-500/30 dark:text-red-400",
  error:    "bg-orange-500/15 text-orange-600 border-orange-500/30 dark:text-orange-400",
  warning:  "bg-yellow-500/15 text-yellow-700 border-yellow-500/30 dark:text-yellow-400",
  info:     "bg-blue-500/15 text-blue-600 border-blue-500/30 dark:text-blue-400",
  debug:    "bg-muted text-muted-foreground border-border",
};

const SeverityBadge = ({ severity }: { severity: Severity }) => (
  <Badge variant="outline" className={cn("font-medium", SEVERITY_STYLES[severity])}>
    {severity}
  </Badge>
);

export default SeverityBadge;