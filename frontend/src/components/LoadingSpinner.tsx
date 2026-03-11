export default function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <div className="spinner" />
      <p className="text-sm text-dark-muted">Running query...</p>
    </div>
  );
}
