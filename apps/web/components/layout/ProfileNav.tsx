"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/dashboard/profile", label: "Overview" },
  { href: "/dashboard/profile/skills", label: "Skills" },
  { href: "/dashboard/profile/experience", label: "Experience" },
  { href: "/dashboard/profile/education", label: "Education" },
];

export function ProfileNav() {
  const pathname = usePathname();
  return (
    <div className="mb-6 flex flex-wrap gap-2">
      {LINKS.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={cn(
            "rounded-full border px-3 py-1 text-sm transition",
            pathname === link.href
              ? "border-transparent bg-ai-light font-medium text-ink"
              : "border-line text-muted hover:text-ink",
          )}
        >
          {link.label}
        </Link>
      ))}
    </div>
  );
}
