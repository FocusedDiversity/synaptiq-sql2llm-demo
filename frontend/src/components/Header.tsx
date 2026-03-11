export default function Header() {
  return (
    <header className="bg-dark-surface border-b border-dark-border px-6 py-4 flex items-center gap-4 shrink-0">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-accent flex items-center justify-center font-bold text-white text-lg select-none">
          S
        </div>
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight leading-tight">
            Synaptiq SQL2LLM
          </h1>
          <p className="text-xs text-dark-muted leading-tight">
            Natural language to SQL, powered by AI
          </p>
        </div>
      </div>
    </header>
  );
}
