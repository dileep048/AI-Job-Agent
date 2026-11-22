export function Spinner({ label = "Loading..." }: { label?: string }) {
  return (
    <div className="flex items-center justify-center py-12 text-sm text-muted" role="status">
      <span className="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-line border-t-[#FACC15]" />
      {label}
    </div>
  );
}
