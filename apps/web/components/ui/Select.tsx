export function Select({
  label,
  error,
  children,
  ...props
}: React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string; error?: string }) {
  return (
    <label className="block space-y-1.5">
      {label ? <span className="text-sm font-medium text-ink">{label}</span> : null}
      <select
        className="w-full rounded-button border border-line bg-white px-3 py-2 text-sm outline-none transition focus:border-ai-blue"
        {...props}
      >
        {children}
      </select>
      {error ? <span className="text-xs text-error">{error}</span> : null}
    </label>
  );
}
