const BENEFITS = ["Save time", "Apply consistently", "Discover more opportunities", "Stay organized"];

export function Benefits() {
  return (
    <section className="bg-background-soft">
      <div className="mx-auto max-w-6xl px-4 py-20 md:px-6">
        <h2 className="max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
          Stop spending hours applying to jobs.
        </h2>
        <p className="mt-4 max-w-xl text-lg text-muted">
          You focus on your career. Your AI agent handles the repetitive work.
        </p>
        <ul className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {BENEFITS.map((item) => (
            <li key={item} className="rounded-card border border-line bg-white px-5 py-6 shadow-card">
              <span className="mb-3 block h-2 w-8 rounded-full bg-[#FACC15]" />
              <p className="font-semibold">{item}</p>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
