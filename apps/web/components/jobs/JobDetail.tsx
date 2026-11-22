"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";

import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Spinner } from "@/components/ui/Spinner";
import { getJob } from "@/lib/api/jobs";
import { formatDate, htmlToPlainText } from "@/lib/utils";

export function JobDetail() {
  const params = useParams<{ id: string }>();
  const query = useQuery({ queryKey: ["job", params.id], queryFn: () => getJob(params.id) });

  if (query.isLoading) return <Spinner />;
  if (query.error || !query.data) return <ErrorState message="Job not found." />;

  const job = query.data;
  const salary =
    job.salary_min || job.salary_max
      ? `${job.salary_currency ?? ""} ${job.salary_min ?? "—"}–${job.salary_max ?? "—"}`.trim()
      : "Not listed";

  return (
    <div className="space-y-6">
      <Link href="/dashboard/jobs" className="text-sm text-muted hover:text-ink">
        ← All jobs
      </Link>
      <div>
        <h1 className="text-2xl font-semibold">{job.title}</h1>
        <p className="mt-1 text-muted">{job.company_name}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <dl className="space-y-2 text-sm">
            <div>
              <dt className="text-muted">Location</dt>
              <dd>{job.location ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted">Workplace</dt>
              <dd>{job.workplace_type ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted">Employment</dt>
              <dd>{job.employment_type ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted">Salary</dt>
              <dd>{salary}</dd>
            </div>
            <div>
              <dt className="text-muted">Posted</dt>
              <dd>{formatDate(job.posted_at)}</dd>
            </div>
            <div>
              <dt className="text-muted">Source</dt>
              <dd>{job.source_name ?? job.source_type ?? "Manual"}</dd>
            </div>
          </dl>
        </Card>
        <Card className="bg-ai-light/50">
          <p className="text-sm font-medium">AI Match — Coming Soon</p>
          <p className="mt-2 text-sm text-muted">
            Fit scoring against your profile will be added in a later sprint.
          </p>
        </Card>
      </div>
      <Card>
        <h2 className="font-semibold">Description</h2>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-ink">
          {job.description ? htmlToPlainText(job.description) : "No description provided."}
        </p>
      </Card>
      <Card>
        <h2 className="font-semibold">Required skills</h2>
        {job.skills.length === 0 ? (
          <p className="mt-2 text-sm text-muted">No structured skills were ingested for this job.</p>
        ) : (
          <ul className="mt-3 flex flex-wrap gap-2">
            {job.skills.map((skill) => (
              <li key={skill.id} className="rounded-full bg-ai-light px-3 py-1 text-sm">
                {skill.skill_name}
              </li>
            ))}
          </ul>
        )}
      </Card>
      {job.source_url ? (
        <a
          href={job.source_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex rounded-button bg-[#FACC15] px-4 py-2.5 text-sm font-semibold text-ink"
        >
          View original posting
        </a>
      ) : null}
    </div>
  );
}
