export function TrustSection() {
  const items = [
    "AI-powered job matching",
    "Automated applications",
    "Application tracking",
    "Smart resume customization",
  ];
  return (
    <section className="border-y border-line bg-background-soft">
      <div className="mx-auto max-w-6xl px-4 py-10 md:px-6">
        <p className="text-center text-sm font-medium text-muted">Built for modern job seekers</p>
        <ul className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {items.map((item) => (
            <li
              key={item}
              className="flex items-center gap-2 rounded-card border border-line bg-white px-4 py-3 text-sm text-ink"
            >
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-[#FACC15] text-xs font-bold">
                ✓
              </span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
