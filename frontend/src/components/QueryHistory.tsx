import type { HistoryEntry } from "../types";

interface QueryHistoryProps {
  history: HistoryEntry[];
  onSelect: (query: string) => void;
  onClear: () => void;
}

function formatTime(ts: number): string {
  const d = new Date(ts);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMin = Math.floor(diffMs / 60000);

  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;

  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;

  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function QueryHistory({ history, onSelect, onClear }: QueryHistoryProps) {
  if (history.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-dark-muted">
        No queries yet. Try asking a question!
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-4 py-3 border-b border-dark-border">
        <h2 className="text-xs font-semibold text-dark-muted uppercase tracking-wide">
          History
        </h2>
        <button
          onClick={onClear}
          className="text-xs text-dark-muted hover:text-red-400 transition-colors"
        >
          Clear
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {history.map((entry, i) => (
          <button
            key={`${entry.timestamp}-${i}`}
            onClick={() => onSelect(entry.query)}
            className="w-full text-left px-4 py-3 border-b border-dark-border hover:bg-dark-border/30 transition-colors group"
          >
            <p className="text-sm text-dark-text group-hover:text-accent transition-colors line-clamp-2 leading-snug">
              {entry.query}
            </p>
            <p className="text-xs text-dark-muted mt-1">{formatTime(entry.timestamp)}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
