import { useState, useCallback } from "react";
import Header from "./components/Header";
import QueryInput from "./components/QueryInput";
import SuggestionChips from "./components/SuggestionChips";
import ResultsPanel from "./components/ResultsPanel";
import QueryHistory from "./components/QueryHistory";
import LoadingSpinner from "./components/LoadingSpinner";
import ErrorDisplay from "./components/ErrorDisplay";
import { useQuery } from "./hooks/useQuery";
import { useQueryHistory } from "./hooks/useQueryHistory";

export default function App() {
  const { loading, result, error, execute } = useQuery();
  const { history, addEntry, clearHistory } = useQueryHistory();
  const [currentQuery, setCurrentQuery] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleSubmit = useCallback(
    async (query: string) => {
      setCurrentQuery(query);
      const res = await execute(query);
      if (res && res.generated_sql) {
        addEntry(query, res.generated_sql);
      }
    },
    [execute, addEntry]
  );

  const handleSuggestionSelect = useCallback(
    (query: string) => {
      setCurrentQuery(query);
      handleSubmit(query);
    },
    [handleSubmit]
  );

  const handleHistorySelect = useCallback(
    (query: string) => {
      setCurrentQuery(query);
      handleSubmit(query);
      setSidebarOpen(false);
    },
    [handleSubmit]
  );

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <Header />

      <div className="flex-1 flex overflow-hidden relative">
        {/* Mobile sidebar toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="lg:hidden fixed bottom-4 right-4 z-30 w-12 h-12 rounded-full bg-accent text-white flex items-center justify-center shadow-lg hover:bg-accent-hover transition-colors"
          aria-label="Toggle history"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </button>

        {/* Sidebar overlay for mobile */}
        {sidebarOpen && (
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-20"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          } lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-20 w-72 bg-dark-surface border-r border-dark-border transition-transform duration-200 lg:shrink-0 overflow-hidden`}
        >
          <QueryHistory
            history={history}
            onSelect={handleHistorySelect}
            onClear={clearHistory}
          />
        </aside>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
            <SuggestionChips onSelect={handleSuggestionSelect} />

            <QueryInput
              onSubmit={handleSubmit}
              loading={loading}
              generatedSql={result?.generated_sql || null}
              initialQuery={currentQuery}
            />

            {loading && <LoadingSpinner />}

            {error && !loading && <ErrorDisplay message={error} />}

            {result && !loading && !result.error && (
              <ResultsPanel result={result} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
