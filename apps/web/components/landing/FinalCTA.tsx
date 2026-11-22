import Link from "next/link";

import { buttonClassName } from "@/components/ui/Button";

export function FinalCTA() {
  return (
    <section className="bg-ai-light">
      <div className="mx-auto max-w-4xl px-4 py-20 text-center md:px-6">
        <h2 className="text-3xl font-semibold tracking-tight md:text-5xl">
          Let your next job search
          <br />
          run on autopilot.
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-muted">
          Set your preferences, activate your AI agent, and spend less time applying.
        </p>
        <Link href="/register" className={buttonClassName("primary", "mt-8 px-6 py-3")}>
          Start Your Job Search →
        </Link>
      </div>
    </section>
  );
}
