export function ErrorState({ message }: { message: string }) {
  return (
    <div
      className="rounded-card border border-error/20 bg-error/10 px-4 py-3 text-sm text-error"
      role="alert"
    >
      {message}
    </div>
  );
}
