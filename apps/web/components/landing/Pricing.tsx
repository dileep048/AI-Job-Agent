export function Pricing() {
  return (
    <section id="pricing" className="scroll-mt-24 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-20 text-center md:px-6">
        <p className="text-sm font-semibold text-ai-blue">Pricing</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
          Simple plans for your job search
        </h2>
        <p className="mx-auto mt-3 max-w-lg text-muted">
          Choose the plan that fits your search. Paid plans will be published here when billing is ready.
        </p>
        <div className="mx-auto mt-10 max-w-md rounded-card border border-line bg-background-soft p-8">
          <p className="text-lg font-semibold">Coming Soon</p>
          <p className="mt-2 text-sm text-muted">
            You can create an account and set up your profile and resume today. Agent matching and
            automated applications will follow.
          </p>
        </div>
      </div>
    </section>
  );
}
