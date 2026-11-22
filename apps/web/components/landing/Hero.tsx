import Link from "next/link";

import { buttonClassName } from "@/components/ui/Button";

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-white">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--ai-light),_transparent_42%)]" />
      <div className="relative mx-auto grid max-w-6xl items-center gap-12 px-4 py-16 md:grid-cols-2 md:px-6 md:py-24">
        <div className="animate-fade-up">
          <p className="mb-4 inline-flex items-center rounded-full bg-ai-light px-3 py-1 text-sm font-medium text-ink">
            Your AI job search agent
          </p>
          <h1 className="text-[40px] font-semibold leading-[1.1] tracking-tight text-ink md:text-6xl lg:text-7xl">
            Your AI Agent for
            <br />
            the <span className="rounded-md bg-[#FACC15] px-2">Job Search.</span>
          </h1>
          <p className="mt-6 max-w-lg text-lg leading-relaxed text-muted">
            Let AI find the right jobs, match them to your profile, and automate the repetitive work of
            applying.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/register" className={buttonClassName("primary", "px-5 py-3")}>
              Start Applying with AI →
            </Link>
            <Link href="/#how-it-works" className={buttonClassName("secondary", "px-5 py-3")}>
              See How It Works
            </Link>
          </div>
        </div>
        <HeroVisual />
      </div>
    </section>
  );
}

function HeroVisual() {
  return (
    <div className="animate-fade-up rounded-section border border-line bg-white p-4 shadow-soft" aria-hidden>
      <div className="mb-4 flex items-center justify-between rounded-card bg-ai-light px-4 py-3">
        <div>
          <p className="text-sm font-semibold text-ink">AI Agent</p>
          <p className="text-xs text-muted">Searching and matching roles</p>
        </div>
        <span className="rounded-full bg-[#FACC15] px-2.5 py-1 text-xs font-semibold text-[#111827]">Live</span>
      </div>
      <div className="space-y-3">
        {[
          { role: "Senior Backend Engineer", match: "92%", status: "Strong match" },
          { role: "Staff Platform Engineer", match: "86%", status: "Ready to review" },
          { role: "Full-stack Engineer", match: "74%", status: "In review" },
        ].map((job) => (
          <div key={job.role} className="rounded-card border border-line p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="font-medium text-ink">{job.role}</p>
                <p className="text-sm text-muted">{job.status}</p>
              </div>
              <span className="rounded-full bg-ai-light px-2 py-1 text-xs font-semibold text-ink">
                {job.match}
              </span>
            </div>
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-background-soft">
              <div className="h-full rounded-full bg-[#FACC15]" style={{ width: job.match }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
