import { Card } from "@/components/ui/Card";

export default function AgentPage() {
  return (
    <Card className="bg-ai-light/50">
      <p className="text-sm font-medium">AI Agent</p>
      <h1 className="mt-1 text-2xl font-semibold">Agent activity</h1>
      <p className="mt-2 text-sm text-muted">
        Resume customization and auto-apply will be added in later sprints. This page will show what
        the agent is searching, matching, and preparing.
      </p>
    </Card>
  );
}
