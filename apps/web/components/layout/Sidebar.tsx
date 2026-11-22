"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { Logo } from "@/components/brand/Logo";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/dashboard/jobs", label: "Jobs" },
  { href: "/dashboard/applications", label: "Applications" },
  { href: "/dashboard/resumes", label: "Resume" },
  { href: "/dashboard/profile", label: "Profile" },
  { href: "/dashboard/agent", label: "AI Agent" },
  { href: "/dashboard/settings", label: "Settings" },
];

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();
  return (
    <nav className="flex-1 space-y-1 px-3" aria-label="Dashboard">
      {NAV.map((item) => {
        const active =
          item.href === "/dashboard" ? pathname === "/dashboard" : pathname.startsWith(item.href);
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "block rounded-xl px-3 py-2 text-sm transition",
              active ? "bg-ai-light font-medium text-ink" : "text-muted hover:bg-background-soft hover:text-ink",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="flex h-full w-60 flex-col border-r border-line bg-white">
      <div className="px-5 py-6">
        <Logo href="/dashboard" />
      </div>
      <NavLinks />
      <div className="border-t border-line p-4">
        <p className="truncate text-sm font-medium">{user?.name ?? user?.email}</p>
        <p className="truncate text-xs text-muted">{user?.email}</p>
        <button className="mt-3 text-sm text-muted hover:text-ink" onClick={logout}>
          Log out
        </button>
      </div>
    </aside>
  );
}

export function MobileDashboardNav() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-line bg-white px-4 py-3 md:hidden">
      <div className="flex items-center justify-between">
        <Logo href="/dashboard" />
        <button
          type="button"
          className="rounded-button border border-line px-3 py-1.5 text-sm"
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          {open ? "Close" : "Menu"}
        </button>
      </div>
      {open ? (
        <div className="mt-3 border-t border-line pt-3">
          <NavLinks onNavigate={() => setOpen(false)} />
          <p className="mt-3 truncate px-3 text-xs text-muted">{user?.email}</p>
          <button className="mt-2 px-3 text-sm text-muted" onClick={logout}>
            Log out
          </button>
        </div>
      ) : null}
    </header>
  );
}
