const FEATURES = [
  {
    title: "AI Job Matching",
    body: "Find jobs based on your skills, experience, location and preferences.",
  },
  {
    title: "Automated Applications",
    body: "Let your AI agent handle repetitive application workflows.",
  },
  {
    title: "Smart Resume Matching",
    body: "Adapt your resume and profile to relevant job requirements.",
  },
  {
    title: "Application Tracking",
    body: "Track every application from one dashboard.",
  },
  {
    title: "AI Agent Activity",
    body: "See what your agent is currently searching, matching and applying to.",
  },
  {
    title: "Job Preferences",
    body: "Set salary, location, role, experience and other preferences.",
  },
];

export function Features() {
  return (
    <section id="features" className="scroll-mt-24 bg-background-soft">
      <div className="mx-auto max-w-6xl px-4 py-20 md:px-6">
        <p className="text-sm font-semibold text-ai-blue">Features</p>
        <h2 className="mt-2 max-w-xl text-3xl font-semibold tracking-tight md:text-4xl">
          Everything you need for a calmer job search
        </h2>
        <div className="mt-10 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <article
              key={feature.title}
              className="rounded-card border border-line bg-white p-6 shadow-card transition hover:-translate-y-0.5 hover:shadow-soft"
            >
              <span className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ai-light text-lg">
                ✦
              </span>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted">{feature.body}</p>
              <div className="mt-4 h-1.5 w-8 rounded-full bg-[#FACC15]" />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
