// src/components/logs/LogTable.tsx
import { useNavigate } from "react-router-dom";
import type  { LogEntry } from "../../types/log";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import SeverityBadge from "@/components/logs/SeverityBadge";
import { Loader2 } from "lucide-react";

interface LogTableProps {
  logs: LogEntry[];
  loading?: boolean;
}

const LogTable = ({ logs, loading }: LogTableProps) => {
  const navigate = useNavigate();

  if (loading) {
    return (
      <div className="py-12 flex items-center justify-center text-muted-foreground gap-2">
        <Loader2 className="h-4 w-4 animate-spin" /> Chargement des logs...
      </div>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="py-12 text-center text-sm text-muted-foreground">
        Aucun log trouvé.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border shadow-sm">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/40">
            <TableHead className="whitespace-nowrap">Date</TableHead>
            <TableHead className="whitespace-nowrap">Sévérité</TableHead>
            <TableHead className="whitespace-nowrap">Source</TableHead>
            <TableHead className="whitespace-nowrap">Hôte</TableHead>
            <TableHead>Message</TableHead>
            <TableHead className="whitespace-nowrap">Tags</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {logs.map((log) => (
            <TableRow
              key={log.id}
              className="cursor-pointer transition-colors hover:bg-muted/40"
              onClick={() => navigate(`/logs/${log.id}`)}
            >
              <TableCell className="whitespace-nowrap font-mono text-xs text-muted-foreground">
                {new Date(log.timestamp).toLocaleString("fr-FR")}
              </TableCell>
              <TableCell><SeverityBadge severity={log.severity} /></TableCell>
              <TableCell className="font-mono text-xs">{log.source_ip}</TableCell>
              <TableCell className="text-xs">{log.host}</TableCell>
              <TableCell className="max-w-md truncate text-sm">{log.raw_message}</TableCell>
              <TableCell>
                <div className="flex max-w-[160px] flex-wrap gap-1">
                  {log.tags.slice(0, 2).map((tag) => (
                    <span key={tag} className="rounded-full bg-muted px-2 py-0.5 text-xs">{tag}</span>
                  ))}
                  {log.tags.length > 2 && (
                    <span className="text-xs text-muted-foreground">+{log.tags.length - 2}</span>
                  )}
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default LogTable;