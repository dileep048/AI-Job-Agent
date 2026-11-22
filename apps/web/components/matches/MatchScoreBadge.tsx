import { cn } from "@/lib/utils";

export function recommendationClass(value: string | null | undefined) {
  if (value === "APPLY") return "bg-emerald-50 text-emerald-800";
  if (value === "CONSIDER") return "bg-amber-50 text-amber-800";
  if (value === "SKIP") return "bg-slate-100 text-slate-600";
  return "bg-ai-light text-ink";
}

export function MatchScoreBadge({
  score,
  recommendation,
}: {
  score: number | null | undefined;
  recommendation?: string | null;
}) {
  if (score == null) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
        recommendationClass(recommendation),
      )}
    >
      {Math.round(score)} · {recommendation ?? "Scored"}
    </span>
  );
}
