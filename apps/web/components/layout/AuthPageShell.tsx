import { Logo } from "@/components/brand/Logo";

export function AuthPageShell({ children }: { children: React.ReactNode }) {
  return (
    <main className="relative min-h-screen bg-background-soft">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_var(--ai-light),_transparent_45%)]" />
      <div className="relative mx-auto flex max-w-md flex-col px-4 py-10">
        <Logo />
        <div className="mt-10">{children}</div>
      </div>
    </main>
  );
}
