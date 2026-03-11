import { useState, useCallback, useEffect } from "react";
import type { HistoryEntry } from "../types";

const STORAGE_KEY = "synaptiq-query-history";
const MAX_ENTRIES = 20;

function loadHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed as HistoryEntry[];
  } catch {
    return [];
  }
}

function saveHistory(entries: HistoryEntry[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

export function useQueryHistory() {
  const [history, setHistory] = useState<HistoryEntry[]>(loadHistory);

  useEffect(() => {
    saveHistory(history);
  }, [history]);

  const addEntry = useCallback((query: string, generated_sql: string) => {
    setHistory((prev) => {
      const entry: HistoryEntry = {
        query,
        timestamp: Date.now(),
        generated_sql,
      };
      const next = [entry, ...prev.filter((e) => e.query !== query)];
      return next.slice(0, MAX_ENTRIES);
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
  }, []);

  return { history, addEntry, clearHistory };
}
