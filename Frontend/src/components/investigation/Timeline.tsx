// src/components/investigation/Timeline.tsx
import type { TimelineEntry } from "../../types/event";

interface TimelineProps {
  entries: TimelineEntry[];
  onSelect: (entry: TimelineEntry) => void;
  selected?: string;
}

const Timeline = ({ entries, onSelect, selected }: TimelineProps) => {
  if (entries.length === 0) {
    return (
      <div className="py-8 text-center text-gray-600 text-sm">
        Aucun événement sur cette période.
      </div>
    );
  }

  return (
    <div className="relative pl-6">
      {/* Ligne verticale */}
      <div className="absolute left-2 top-0 bottom-0 w-px bg-gray-800" />

      <ul className="space-y-3">
        {entries.map((entry) => {
          const isSelected = selected === entry.event.id;
          return (
            <li
              key={entry.event.id}
              onClick={() => onSelect(entry)}
              className={`relative flex flex-col gap-1 p-3 rounded-lg border cursor-pointer transition-colors ${
                isSelected
                  ? "bg-cyan-900/20 border-cyan-800"
                  : "bg-gray-900 border-gray-800 hover:border-gray-700"
              }`}
            >
              {/* Dot */}
              <div
                className={`absolute -left-[1.35rem] top-4 w-2 h-2 rounded-full border-2 ${
                  entry.event.marked
                    ? "bg-red-500 border-red-400"
                    : "bg-gray-600 border-gray-800"
                }`}
              />

              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-gray-400">
                  {new Date(entry.event.timestamp).toLocaleTimeString("fr-FR")}
                </span>
                <span className="text-xs text-gray-600">{entry.event.type}</span>
              </div>

              <p className="text-sm text-gray-200 leading-snug">
                {entry.event.description}
              </p>

              {entry.event.sourceIp && (
                <span className="text-xs text-gray-500 font-mono">
                  {entry.event.sourceIp}
                  {entry.event.destinationIp && ` → ${entry.event.destinationIp}`}
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Timeline;