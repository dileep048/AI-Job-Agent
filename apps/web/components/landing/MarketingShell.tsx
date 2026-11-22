import { LandingFooter } from "@/components/landing/Footer";
import { LandingNavbar } from "@/components/landing/Navbar";

export function MarketingShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-white">
      <LandingNavbar />
      <main className="mx-auto max-w-3xl px-4 py-16 md:px-6">
        <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
        <div className="mt-6 space-y-4 text-muted">{children}</div>
      </main>
      <LandingFooter />
    </div>
  );
}
