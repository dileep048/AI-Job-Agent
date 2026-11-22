import type { Metadata } from "next";

import { MarketingShell } from "@/components/landing/MarketingShell";

export const metadata: Metadata = { title: "Terms" };

export default function TermsPage() {
  return (
    <MarketingShell title="Terms">
      <p>
        AI Job Agent is provided as an early product. Features such as automated applications are not
        guaranteed until they ship. Formal terms of service will be published before a paid public
        launch.
      </p>
    </MarketingShell>
  );
}
