export function AgentShowcase() {
  return (
    <section className="bg-white">
      <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 py-20 md:grid-cols-2 md:px-6">
        <div>
          <p className="text-sm font-semibold text-ai-blue">Agent activity</p>
          <h2 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
            Watch your AI agent work
          </h2>
          <p className="mt-4 text-muted">
            The dashboard shows search, matching, and application progress in one place — so you stay in
            control without doing the repetitive parts yourself.
          </p>
        </div>
        <div className="rounded-section border border-line bg-ai-light p-3 shadow-soft">
          <div className="rounded-card bg-white p-6">
            <div className="mb-5 flex items-center justify-between">
              <p className="font-semibold">✨ AI Agent</p>
              <span className="text-sm text-muted">Working…</span>
            </div>
            <ul className="space-y-4 text-sm">
              <li className="flex items-center justify-between">
                <span>Searching jobs...</span>
                <span className="font-semibold text-success">✓</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Matching your profile...</span>
                <span className="font-semibold text-success">✓</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Preparing application...</span>
                <span className="h-2.5 w-2.5 rounded-full bg-[#FACC15] animate-pulse-dot" aria-hidden />
              </li>
            </ul>
            <div className="mt-6 grid grid-cols-3 gap-3 border-t border-line pt-4 text-center">
              <div>
                <p className="text-lg font-semibold">24</p>
                <p className="text-xs text-muted">jobs reviewed</p>
              </div>
              <div>
                <p className="text-lg font-semibold">8</p>
                <p className="text-xs text-muted">strong matches</p>
              </div>
              <div>
                <p className="text-lg font-semibold">3</p>
                <p className="text-xs text-muted">ready to apply</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
