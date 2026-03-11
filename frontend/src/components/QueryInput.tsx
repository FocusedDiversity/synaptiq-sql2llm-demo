import { useState, useCallback, type FormEvent } from "react";

interface QueryInputProps {
  onSubmit: (query: string) => void;
  loading: boolean;
  generatedSql: string | null;
  initialQuery?: string;
}

export default function QueryInput({
  onSubmit,
  loading,
  generatedSql,
  initialQuery = "",
}: QueryInputProps) {
  const [query, setQuery] = useState(initialQuery);

  const handleSubmit = useCallback(
    (e: FormEvent) => {
      e.preventDefault();
      const trimmed = query.trim();
      if (!trimmed || loading) return;
      onSubmit(trimmed);
    },
    [query, loading, onSubmit]
  );

  // Allow parent to set query via initialQuery changes
  // We use a key-like approach: when initialQuery changes externally, update local state
  const [prevInitial, setPrevInitial] = useState(initialQuery);
  if (initialQuery !== prevInitial) {
    setPrevInitial(initialQuery);
    setQuery(initialQuery);
  }

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a question about your data..."
          rows={2}
          className="flex-1 resize-none rounded-lg border border-dark-border bg-dark-surface px-4 py-3 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-colors"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="shrink-0 rounded-lg bg-accent px-6 py-3 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-40 disabled:cursor-not-allowed transition-colors sm:self-end"
        >
          {loading ? "Running..." : "Submit"}
        </button>
      </form>

      {generatedSql && (
        <div className="rounded-lg border border-dark-border bg-dark-bg p-3">
          <p className="text-xs text-dark-muted mb-1.5 font-medium uppercase tracking-wide">
            Generated SQL
          </p>
          <pre className="text-sm text-blue-300 whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto">
            {generatedSql}
          </pre>
        </div>
      )}
    </div>
  );
}
