"use client";

import Link from "next/link";
import { useState } from "react";

import { Logo } from "@/components/brand/Logo";
import { buttonClassName } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/#how-it-works", label: "How it works" },
  { href: "/#features", label: "Features" },
  { href: "/#pricing", label: "Pricing" },
  { href: "/#faq", label: "FAQ" },
];

export function LandingNavbar() {
  const [open, setOpen] = useState(false);
  const { user } = useAuth();
  const ctaHref = user ? "/dashboard" : "/register";
  const ctaLabel = user ? "Open dashboard" : "Get Started";

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 md:px-6">
        <Logo />
        <nav className="hidden items-center gap-8 md:flex" aria-label="Primary">
          {LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="text-sm text-muted hover:text-ink">
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="hidden items-center gap-3 md:flex">
          {!user ? (
            <Link href="/login" className="text-sm font-medium text-ink hover:text-muted">
              Log in
            </Link>
          ) : null}
          <Link href={ctaHref} className={buttonClassName("primary")}>
            {ctaLabel}
          </Link>
        </div>
        <button
          type="button"
          className="rounded-button border border-line px-3 py-2 text-sm md:hidden"
          aria-expanded={open}
          aria-controls="mobile-nav"
          onClick={() => setOpen((value) => !value)}
        >
          {open ? "Close" : "Menu"}
        </button>
      </div>
      <div
        id="mobile-nav"
        className={cn("border-t border-line bg-white px-4 py-4 md:hidden", open ? "block" : "hidden")}
      >
        <nav className="flex flex-col gap-3" aria-label="Mobile">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm text-ink"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </Link>
          ))}
          {!user ? (
            <Link href="/login" className="text-sm text-ink" onClick={() => setOpen(false)}>
              Log in
            </Link>
          ) : null}
          <Link href={ctaHref} className={buttonClassName("primary", "w-full")} onClick={() => setOpen(false)}>
            {ctaLabel}
          </Link>
        </nav>
      </div>
    </header>
  );
}
