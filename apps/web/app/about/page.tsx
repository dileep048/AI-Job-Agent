import type { Metadata } from "next";

import { MarketingShell } from "@/components/landing/MarketingShell";

export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  return (
    <MarketingShell title="About">
      <p>
        AI Job Agent is a workspace for job seekers who want matching, tracking, and less repetitive
        application work. You can create an account, complete your profile, and store structured
        resumes today.
      </p>
      <p>Automated job search and apply flows are being built on this foundation.</p>
    </MarketingShell>
  );
}
