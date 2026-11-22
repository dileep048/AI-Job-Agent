import Link from "next/link";

import { cn } from "@/lib/utils";

export function Logo({
  href = "/",
  className,
}: {
  href?: string;
  className?: string;
}) {
  return (
    <Link href={href} className={cn("inline-flex items-center gap-2", className)}>
      <span
        aria-hidden
        className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#FACC15] text-sm font-bold text-[#111827]"
      >
        AI
      </span>
      <span className="text-base font-semibold tracking-tight text-ink">AI Job Agent</span>
    </Link>
  );
}
