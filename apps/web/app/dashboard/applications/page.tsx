import { Card } from "@/components/ui/Card";

export default function ApplicationsPage() {
  return (
    <Card>
      <h1 className="text-2xl font-semibold">Applications</h1>
      <p className="mt-2 text-sm text-muted">
        Application tracking will be added in a later sprint. Submitted and in-progress applications
        will appear here.
      </p>
    </Card>
  );
}
