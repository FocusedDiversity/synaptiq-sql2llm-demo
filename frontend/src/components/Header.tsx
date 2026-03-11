export default function Header() {
  return (
    <header className="bg-dark-surface border-b border-dark-border px-6 py-4 flex items-center gap-4 shrink-0">
      <div className="flex items-center gap-3">
        <img
          src="/sparkle_logo.png"
          alt="Sparkle Car Wash"
          className="h-[120px] w-auto"
        />
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight leading-tight">
            Proof of Concept (POC)
          </h1>
          <p className="text-xs text-dark-muted leading-tight">
            Natural language to SQL, powered by AI
          </p>
        </div>
      </div>
    </header>
  );
}
