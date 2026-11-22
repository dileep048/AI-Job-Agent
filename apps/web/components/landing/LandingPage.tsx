import { AgentShowcase } from "@/components/landing/AgentShowcase";
import { Benefits } from "@/components/landing/Benefits";
import { FAQ } from "@/components/landing/FAQ";
import { Features } from "@/components/landing/Features";
import { FinalCTA } from "@/components/landing/FinalCTA";
import { LandingFooter } from "@/components/landing/Footer";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { LandingNavbar } from "@/components/landing/Navbar";
import { Pricing } from "@/components/landing/Pricing";
import { TrustSection } from "@/components/landing/TrustSection";

export function LandingPage() {
  return (
    <div className="bg-white text-ink">
      <LandingNavbar />
      <main>
        <Hero />
        <TrustSection />
        <HowItWorks />
        <Features />
        <AgentShowcase />
        <Benefits />
        <Pricing />
        <FAQ />
        <FinalCTA />
      </main>
      <LandingFooter />
    </div>
  );
}
