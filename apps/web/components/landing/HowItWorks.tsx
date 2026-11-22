const STEPS = [
  {
    n: "01",
    title: "Create your profile",
    body: "Tell the AI about your experience, skills and target roles.",
  },
  {
    n: "02",
    title: "AI finds matching jobs",
    body: "Your agent continuously searches for jobs matching your preferences.",
  },
  {
    n: "03",
    title: "AI applies for you",
    body: "The agent handles repetitive application steps and keeps your applications organized.",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-24 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-20 md:px-6">
        <p className="text-sm font-semibold text-ai-blue">How it works</p>
        <h2 className="mt-2 text-3xl font-semibold tracking-tight md:text-4xl">
          Three steps from profile to applications
        </h2>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {STEPS.map((step) => (
            <article key={step.n} className="rounded-card border border-line bg-background-soft p-6">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ai-light text-sm font-bold text-ink">
                {step.n}
              </span>
              <h3 className="mt-4 text-lg font-semibold">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{step.body}</p>
              <div className="mt-5 h-1.5 w-12 rounded-full bg-[#FACC15]" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
