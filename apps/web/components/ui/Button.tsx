import { cn } from "@/lib/utils";

const variants = {
  primary:
    "bg-[#FACC15] text-[#111827] shadow-sm hover:bg-[#EAB308] font-semibold",
  secondary: "border border-line bg-white text-ink hover:bg-background-soft",
  danger: "border border-error/20 bg-error/10 text-error hover:bg-error/15",
  ghost: "text-muted hover:text-ink hover:bg-background-soft",
};

export function buttonClassName(
  variant: keyof typeof variants = "primary",
  className?: string,
) {
  return cn(
    "inline-flex items-center justify-center rounded-button px-4 py-2.5 text-sm font-medium transition duration-200 disabled:opacity-50",
    variants[variant],
    className,
  );
}

export function Button({
  className,
  variant = "primary",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: keyof typeof variants;
}) {
  return <button className={buttonClassName(variant, className)} {...props} />;
}
