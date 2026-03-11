import { useEffect, useState } from "react";
import { fetchSuggestions } from "../api/client";
import type { SuggestionCategory } from "../types";

interface SuggestionChipsProps {
  onSelect: (query: string) => void;
}

export default function SuggestionChips({ onSelect }: SuggestionChipsProps) {
  const [categories, setCategories] = useState<SuggestionCategory[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchSuggestions()
      .then((data) => {
        if (!cancelled) setCategories(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load suggestions");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (error) return null;
  if (categories.length === 0) return null;

  return (
    <div className="space-y-3">
      <p className="text-xs text-dark-muted font-medium uppercase tracking-wide">
        Try a sample query
      </p>
      <div className="space-y-2">
        {categories.map((cat) => (
          <div key={cat.category} className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-dark-muted w-24 shrink-0">
              {cat.category}
            </span>
            {cat.queries.map((q) => (
              <button
                key={q}
                onClick={() => onSelect(q)}
                className="rounded-full border border-dark-border bg-dark-surface px-3 py-1 text-xs text-dark-text hover:border-accent hover:text-accent transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
