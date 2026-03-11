interface InsightPanelProps {
  insight: string;
}

export default function InsightPanel({ insight }: InsightPanelProps) {
  return (
    <div className="rounded-lg border border-dark-border bg-dark-surface p-4">
      <div className="flex items-start gap-3">
        <span className="text-2xl leading-none select-none" role="img" aria-label="insight">
          💡
        </span>
        <div>
          <h3 className="text-sm font-semibold text-white mb-1">AI Insight</h3>
          <p className="text-sm text-dark-muted leading-relaxed">{insight}</p>
        </div>
      </div>
    </div>
  );
}
