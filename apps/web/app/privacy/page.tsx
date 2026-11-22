import type { Metadata } from "next";

import { MarketingShell } from "@/components/landing/MarketingShell";

export const metadata: Metadata = { title: "Privacy" };

export default function PrivacyPage() {
  return (
    <MarketingShell title="Privacy">
      <p>
        We store the account, profile, and resume data you submit so the product can run. Files are
        stored through the application storage layer. A full privacy policy will be published before
        public launch.
      </p>
    </MarketingShell>
  );
}
