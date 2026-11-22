"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { createJobSource, getLatestFetchRun, listJobSources, updateJobSource } from "@/lib/api/jobs";
import { formatDateTime } from "@/lib/utils";
import { useToast } from "@/providers/ToastProvider";

export function SourceSettings() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ["job-sources"], queryFn: listJobSources });
  const runQuery = useQuery({ queryKey: ["job-fetch-run"], queryFn: getLatestFetchRun });
  const [url, setUrl] = useState("");
  const [token, setToken] = useState("");
  const [name, setName] = useState("");
  const [sourceType, setSourceType] = useState<"greenhouse" | "lever">("greenhouse");
  const toggle = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      updateJobSource(id, { is_active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["job-sources"] });
      toast.notify("Source updated");
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Update failed", "error"),
  });
  const addSource = useMutation({
    mutationFn: createJobSource,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["job-sources"] });
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["job-fetch-run"] });
      const ingest = result.ingest;
      toast.notify(
        ingest
          ? `Added ${result.name}. Fetched ${ingest.inserted} new jobs.`
          : `Added ${result.name}.`,
      );
      setUrl("");
      setToken("");
      setName("");
    },
    onError: (error) =>
      toast.notify(error instanceof Error ? error.message : "Could not add source", "error"),
  });

  if (query.isLoading) return <Spinner />;
  if (query.error) return <ErrorState message="Could not load job sources." />;
  const sources = query.data ?? [];
  const run = runQuery.data;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="mt-1 text-sm text-muted">
          Add Greenhouse or Lever boards by URL or slug. Active boards are fetched twice daily.
        </p>
      </div>
      <Card>
        <h2 className="font-semibold">Add board source</h2>
        <p className="mt-1 text-sm text-muted">
          Example: https://boards.greenhouse.io/coinbase or https://jobs.lever.co/netflix
        </p>
        <form
          className="mt-4 grid gap-3 md:grid-cols-2"
          onSubmit={(event) => {
            event.preventDefault();
            const trimmedUrl = url.trim();
            const trimmedToken = token.trim();
            if (!trimmedUrl && !trimmedToken) return;
            addSource.mutate({
              url: trimmedUrl || undefined,
              source_type: trimmedUrl ? undefined : sourceType,
              token: trimmedUrl ? undefined : trimmedToken,
              name: name.trim() || undefined,
              fetch_now: true,
            });
          }}
        >
          <div className="md:col-span-2">
            <Input
              label="Board URL"
              placeholder="https://boards.greenhouse.io/company"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
          </div>
          <Input
            label="Display name (optional)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Select
            label="Type if using a slug"
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value as "greenhouse" | "lever")}
          >
            <option value="greenhouse">Greenhouse</option>
            <option value="lever">Lever</option>
          </Select>
          <Input
            label="Board token or Lever slug"
            placeholder="company"
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />
          <div className="flex items-end">
            <Button type="submit" disabled={addSource.isPending || (!url.trim() && !token.trim())}>
              {addSource.isPending ? "Adding…" : "Add source and fetch"}
            </Button>
          </div>
        </form>
      </Card>
      {run ? (
        <Card>
          <p className="text-sm font-medium">Latest catalog fetch</p>
          <p className="mt-2 text-sm text-muted">
            Current fetch: {formatDateTime(run.current_fetch_datetime)}
          </p>
          <p className="text-sm text-muted">Last fetch: {formatDateTime(run.last_fetch_datetime)}</p>
          <p className="mt-2 text-sm text-muted">
            {run.fetched} jobs from {run.boards_succeeded}/{run.boards_attempted} boards
          </p>
        </Card>
      ) : null}
      {sources.length === 0 ? (
        <EmptyState
          title="No sources yet"
          description="Add a Greenhouse or Lever board URL above, or run Fetch on the Jobs page."
        />
      ) : (
        sources.map((source) => (
          <Card key={source.id} className="flex items-center justify-between gap-4">
            <div>
              <p className="font-medium">{source.name}</p>
              <p className="text-sm text-muted">
                {source.source_type}
                {source.external_key ? ` · ${source.external_key}` : ""} ·{" "}
                {source.is_active ? "Active" : "Disabled"}
              </p>
              {source.base_url ? (
                <a
                  className="mt-1 block text-xs text-ai-blue hover:underline"
                  href={source.base_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  {source.base_url}
                </a>
              ) : null}
              <p className="mt-1 text-xs text-muted-text">
                Current fetch: {formatDateTime(source.current_fetch_datetime)} · Last fetch:{" "}
                {formatDateTime(source.last_fetch_datetime)}
              </p>
            </div>
            <Button
              variant="secondary"
              type="button"
              onClick={() => toggle.mutate({ id: source.id, is_active: !source.is_active })}
            >
              {source.is_active ? "Disable" : "Enable"}
            </Button>
          </Card>
        ))
      )}
    </div>
  );
}
