// src/pages/investigation/MarkedEvents.tsx
import { useEffect, useState } from "react";
import type { SecurityEvent } from "../../types/event";
import investigationService from "../../services/investigationService";
import EventDetail from "../../components/investigation/EventDetail";

const MarkedEvents = () => {
  const [events, setEvents]   = useState<SecurityEvent[]>([]);
  const [selected, setSelected] = useState<SecurityEvent | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMarked = async () => {
    setLoading(true);
    try {
      const data = await investigationService.search({ query: "", page: 1, size: 100 });
      setEvents(data.items.filter((e) => e.marked));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchMarked(); }, []);

  const handleMark = async (id: string) => {
    const event   = events.find((e) => e.id === id);
    if (!event) return;
    const updated = await investigationService.markEvent(id, false);
    setEvents((prev) => prev.filter((e) => e.id !== updated.id));
    if (selected?.id === id) setSelected(null);
  };

  return (
    <div className="flex flex-col gap-5 h-full">
      <h1 className="text-white font-medium text-lg">Événements suspects marqués</h1>

      {loading && <p className="text-gray-500 text-sm">Chargement...</p>}
      {!loading && events.length === 0 && (
        <p className="text-gray-600 text-sm">Aucun événement marqué.</p>
      )}

      <div className="flex gap-4 flex-1 min-h-0">
        <div className="flex-1 overflow-y-auto space-y-1">
          {events.map((event) => (
            <div
              key={event.id}
              onClick={() => setSelected(event)}
              className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                selected?.id === event.id
                  ? "bg-red-900/20 border-red-800"
                  : "bg-gray-900 border-red-900/30 hover:border-red-800/60"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono text-gray-400">
                  {new Date(event.timestamp).toLocaleString("fr-FR")}
                </span>
                <span className="text-xs text-gray-600">{event.type}</span>
              </div>
              <p className="text-sm text-gray-200 mt-1 truncate">{event.description}</p>
              {event.sourceIp && (
                <span className="text-xs text-gray-500 font-mono">{event.sourceIp}</span>
              )}
            </div>
          ))}
        </div>

        <div className="w-96 shrink-0 bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-y-auto">
          <EventDetail
            event={selected}
            onMark={handleMark}
            onPivot={() => {}}
          />
        </div>
      </div>
    </div>
  );
};

export default MarkedEvents;