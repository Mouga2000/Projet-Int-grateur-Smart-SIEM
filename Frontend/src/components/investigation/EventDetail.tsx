// src/components/investigation/EventDetail.tsx
import type { SecurityEvent } from "../../types/event";
import Button from "../ui/Button";

interface EventDetailProps {
  event: SecurityEvent | null;
  onMark: (id: string) => void;
  onPivot: (event: SecurityEvent) => void;
}

const EventDetail = ({ event, onMark, onPivot }: EventDetailProps) => {
  if (!event) {
    return (
      <div className="h-full flex items-center justify-center text-gray-600 text-sm">
        Sélectionnez un événement.
      </div>
    );
  }

  const fields: [string, string | undefined][] = [
    ["ID",          event.id],
    ["Type",        event.type],
    ["Source",      event.source],
    ["IP source",   event.sourceIp],
    ["IP dest.",    event.destinationIp],
    ["Utilisateur", event.user],
    ["Hash SHA-256",event.hash],
    ["Alerte liée", event.alertId],
  ];

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-white">Détail de l'événement</h3>
        <div className="flex gap-2">
          <Button
            variant={event.marked ? "danger" : "secondary"}
            size="sm"
            onClick={() => onMark(event.id)}
          >
            {event.marked ? "Retirer le marquage" : "Marquer suspect"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onPivot(event)}
          >
            Pivoter →
          </Button>
        </div>
      </div>

      {/* Timestamp */}
      <p className="text-xs text-gray-500 font-mono">
        {new Date(event.timestamp).toLocaleString("fr-FR")}
      </p>

      {/* Description */}
      <p className="text-sm text-gray-200 leading-relaxed">{event.description}</p>

      {/* Champs */}
      <div className="border border-gray-800 rounded-lg overflow-hidden">
        <table className="w-full text-xs">
          <tbody>
            {fields
              .filter(([, val]) => val)
              .map(([label, val]) => (
                <tr key={label} className="border-b border-gray-800 last:border-0">
                  <td className="px-3 py-2 text-gray-500 w-32">{label}</td>
                  <td className="px-3 py-2 text-gray-200 font-mono break-all">{val}</td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {/* Log brut */}
      {event.rawLog && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Log brut</p>
          <pre className="bg-gray-950 border border-gray-800 rounded-lg p-3 text-xs text-green-400 font-mono overflow-x-auto whitespace-pre-wrap break-all">
            {event.rawLog}
          </pre>
        </div>
      )}
    </div>
  );
};

export default EventDetail;