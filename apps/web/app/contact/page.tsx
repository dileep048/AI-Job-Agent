import type { Metadata } from "next";

import { MarketingShell } from "@/components/landing/MarketingShell";

export const metadata: Metadata = { title: "Contact" };

export default function ContactPage() {
  return (
    <MarketingShell title="Contact">
      <p>
        For product questions, use the in-app dashboard after you create an account. A public support
        channel will be added as the product opens more widely.
      </p>
    </MarketingShell>
  );
}
