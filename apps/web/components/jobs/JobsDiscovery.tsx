"use client";

import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Spinner } from "@/components/ui/Spinner";
import { createJob, importJobFromUrl, ingestGreenhouseAndLever, searchJobs } from "@/lib/api/jobs";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/providers/ToastProvider";
import type { JobSearchParams } from "@/types/jobs";

const PAGE_SIZE = 20;

export function JobsDiscovery() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [draft, setDraft] = useState<JobSearchParams>({
    page: 1,
    page_size: PAGE_SIZE,
    is_active: true,
  });
  const [applied, setApplied] = useState<JobSearchParams>({
    page: 1,
    page_size: PAGE_SIZE,
    is_active: true,
  });
  const [showAdd, setShowAdd] = useState(false);
  const [jobUrl, setJobUrl] = useState("");

  const query = useQuery({
    queryKey: ["jobs", applied],
    queryFn: () => searchJobs(applied),
    placeholderData: keepPreviousData,
  });

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setApplied({
        ...draft,
        q: draft.q?.trim() || undefined,
        location: draft.location?.trim() || undefined,
        company: draft.company?.trim() || undefined,
        page: 1,
        page_size: PAGE_SIZE,
      });
    }, 300);
    return () => window.clearTimeout(timer);
  }, [draft]);

  const create = useMutation({
    mutationFn: createJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      toast.notify("Job added");
      setShowAdd(false);
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Could not add job", "error"),
  });

  const importUrl = useMutation({
    mutationFn: importJobFromUrl,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["job-sources"] });
      toast.notify(`Imported ${result.inserted} new, ${result.updated} updated, ${result.duplicates} unchanged`);
      setJobUrl("");
    },
    onError: (error) =>
      toast.notify(error instanceof Error ? error.message : "Could not import that URL", "error"),
  });

  const ingestAll = useMutation({
    mutationFn: ingestGreenhouseAndLever,
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      queryClient.invalidateQueries({ queryKey: ["job-sources"] });
      toast.notify(
        `Fetched ${result.fetched} jobs from ${result.boards_succeeded} boards (${result.inserted} new)`,
      );
    },
    onError: (error) =>
      toast.notify(error instanceof Error ? error.message : "Board fetch failed", "error"),
  });

  const jobs = query.data?.items ?? [];
  const total = query.data?.total ?? 0;
  const page = applied.page ?? 1;
  const totalPages = Math.max(query.data?.total_pages ?? 0, 1);
  const rangeStart = total === 0 ? 0 : (page - 1) * PAGE_SIZE + 1;
  const rangeEnd = Math.min(page * PAGE_SIZE, total);

  const addForm = useMemo(
    () => ({
      title: "",
      company_name: "",
      location: "",
      workplace_type: "remote",
      employment_type: "full_time",
      description: "",
      source_url: "",
    }),
    [],
  );
  const [form, setForm] = useState(addForm);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">Jobs</h1>
          <p className="mt-1 text-sm text-muted">Search ingested roles. Matching scores come later.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" type="button" onClick={() => setShowAdd((value) => !value)}>
            Add job
          </Button>
        </div>
      </div>

      <Card>
        <h2 className="font-semibold">Import from URL</h2>
        <p className="mt-1 text-sm text-muted">
          Paste a Greenhouse or Lever job posting or careers board URL. The listing is fetched from
          their public APIs and saved in the catalog.
        </p>
        <form
          className="mt-4 flex flex-col gap-3 md:flex-row md:items-end"
          onSubmit={(event) => {
            event.preventDefault();
            const url = jobUrl.trim();
            if (!url) return;
            importUrl.mutate(url);
          }}
        >
          <div className="flex-1">
            <Input
              label="Job or board URL"
              placeholder="https://boards.greenhouse.io/company/jobs/123"
              value={jobUrl}
              onChange={(e) => setJobUrl(e.target.value)}
            />
          </div>
          <Button type="submit" disabled={importUrl.isPending || !jobUrl.trim()}>
            {importUrl.isPending ? "Importing…" : "Import URL"}
          </Button>
        </form>
      </Card>

      {showAdd ? (
        <Card>
          <h2 className="font-semibold">Manual job</h2>
          <form
            className="mt-4 grid gap-3 md:grid-cols-2"
            onSubmit={(event) => {
              event.preventDefault();
              create.mutate({
                ...form,
                source_url: form.source_url.trim() || undefined,
              });
            }}
          >
            <Input label="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            <Input
              label="Company"
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            />
            <Input
              label="Location"
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
            <Input
              label="Job URL"
              placeholder="https://…"
              value={form.source_url}
              onChange={(e) => setForm({ ...form, source_url: e.target.value })}
            />
            <Select
              label="Workplace"
              value={form.workplace_type}
              onChange={(e) => setForm({ ...form, workplace_type: e.target.value })}
            >
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </Select>
            <div className="md:col-span-2">
              <Input
                label="Description"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <Button type="submit" disabled={create.isPending}>
              Save job
            </Button>
          </form>
        </Card>
      ) : null}

      <Card>
        <h2 className="text-sm font-medium">Import from public boards</h2>
        <p className="mt-1 text-sm text-muted">
          Fetches every job from configured Greenhouse and Lever boards. Runs automatically twice a
          day (06:00 and 18:00 UTC). Add extra boards on Settings.
        </p>
        <div className="mt-3 flex flex-col gap-2 md:flex-row">
          <Button
            type="button"
            disabled={importUrl.isPending || ingestAll.isPending}
            onClick={() => ingestAll.mutate()}
          >
            {ingestAll.isPending ? "Fetching boards…" : "Fetch Greenhouse & Lever now"}
          </Button>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[240px_1fr]">
        <Card>
          <h2 className="font-semibold">Filters</h2>
          <form
            className="mt-4 space-y-3"
            onSubmit={(event) => {
              event.preventDefault();
              setApplied({
                ...draft,
                q: draft.q?.trim() || undefined,
                location: draft.location?.trim() || undefined,
                company: draft.company?.trim() || undefined,
                page: 1,
                page_size: PAGE_SIZE,
              });
            }}
          >
            <Input
              label="Search"
              placeholder="Search jobs..."
              value={draft.q ?? ""}
              onChange={(e) => setDraft({ ...draft, q: e.target.value, page: 1 })}
            />
            <Input
              label="Location"
              value={draft.location ?? ""}
              onChange={(e) => setDraft({ ...draft, location: e.target.value, page: 1 })}
            />
            <Input
              label="Company"
              value={draft.company ?? ""}
              onChange={(e) => setDraft({ ...draft, company: e.target.value, page: 1 })}
            />
            <Select
              label="Work type"
              value={draft.workplace_type ?? ""}
              onChange={(e) =>
                setDraft({ ...draft, workplace_type: e.target.value || undefined, page: 1 })
              }
            >
              <option value="">Any</option>
              <option value="remote">Remote</option>
              <option value="hybrid">Hybrid</option>
              <option value="onsite">Onsite</option>
            </Select>
            <Select
              label="Employment"
              value={draft.employment_type ?? ""}
              onChange={(e) =>
                setDraft({ ...draft, employment_type: e.target.value || undefined, page: 1 })
              }
            >
              <option value="">Any</option>
              <option value="full_time">Full-time</option>
              <option value="part_time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </Select>
            <div className="flex gap-2">
              <Button type="submit">Apply filters</Button>
              <Button
                type="button"
                variant="secondary"
                onClick={() => {
                  const reset = { page: 1, page_size: PAGE_SIZE, is_active: true };
                  setDraft(reset);
                  setApplied(reset);
                }}
              >
                Clear
              </Button>
            </div>
          </form>
        </Card>

        <div className="space-y-3">
          {query.isLoading && !query.data ? <Spinner /> : null}
          {query.error ? <ErrorState message="Could not load jobs." /> : null}
          {!query.isLoading && !query.isFetching && !query.error && jobs.length === 0 ? (
            <EmptyState
              title="No jobs yet"
              description="Import a Greenhouse or Lever URL, add a job manually, or fetch public boards."
            />
          ) : null}
          {jobs.map((job) => (
            <Card key={job.id} className="hover:shadow-soft">
              <Link href={`/dashboard/jobs/${job.id}`} className="block">
                <p className="font-semibold">{job.title}</p>
                <p className="text-sm text-muted">{job.company_name}</p>
                <p className="mt-1 text-sm text-muted">
                  {[job.location, job.workplace_type].filter(Boolean).join(" • ") || "Location not listed"}
                </p>
                <p className="mt-2 text-xs text-muted-text">Posted {formatDate(job.posted_at ?? job.created_at)}</p>
              </Link>
            </Card>
          ))}
          {!query.isLoading && !query.error && total > 0 ? (
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <p className="text-sm text-muted">
                Showing {rangeStart}–{rangeEnd} of {total}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="secondary"
                  type="button"
                  disabled={page <= 1}
                  onClick={() =>
                    setApplied((current) => ({
                      ...current,
                      page: (current.page ?? 1) - 1,
                      page_size: PAGE_SIZE,
                    }))
                  }
                >
                  Previous
                </Button>
                <p className="text-sm text-muted">
                  Page {page} of {totalPages}
                </p>
                <Button
                  variant="secondary"
                  type="button"
                  disabled={page >= totalPages}
                  onClick={() =>
                    setApplied((current) => ({
                      ...current,
                      page: (current.page ?? 1) + 1,
                      page_size: PAGE_SIZE,
                    }))
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
