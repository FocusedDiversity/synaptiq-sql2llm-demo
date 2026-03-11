import type { QueryResponse } from "../types";
import DataTable from "./DataTable";
import ChartDisplay from "./ChartDisplay";
import InsightPanel from "./InsightPanel";

interface ResultsPanelProps {
  result: QueryResponse;
}

export default function ResultsPanel({ result }: ResultsPanelProps) {
  const { columns, rows, visualization, insight, truncated } = result;

  if (columns.length === 0 || rows.length === 0) {
    return (
      <div className="text-sm text-dark-muted py-6 text-center">
        No results returned.
      </div>
    );
  }

  const showChart = visualization && visualization.type !== "table";

  return (
    <div className="space-y-4">
      {truncated && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-300">
          Results were truncated. Showing a subset of the data.
        </div>
      )}

      {showChart && (
        <div className="rounded-lg border border-dark-border bg-dark-surface p-4">
          <ChartDisplay columns={columns} rows={rows} visualization={visualization} />
        </div>
      )}

      <div className="rounded-lg border border-dark-border bg-dark-surface p-4">
        <DataTable columns={columns} rows={rows} />
      </div>

      {insight && <InsightPanel insight={insight} />}
    </div>
  );
}
