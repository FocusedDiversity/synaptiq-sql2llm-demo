interface ErrorDisplayProps {
  message: string;
}

export default function ErrorDisplay({ message }: ErrorDisplayProps) {
  return (
    <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm">
      <div className="flex items-start gap-2">
        <span className="text-red-400 font-medium shrink-0">Error:</span>
        <span className="text-red-300">{message}</span>
      </div>
    </div>
  );
}
