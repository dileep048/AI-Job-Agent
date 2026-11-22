"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import { downloadResume, getResume, updateResume } from "@/lib/api/resume";
import { useToast } from "@/providers/ToastProvider";

export function ResumeDetail() {
  const params = useParams<{ id: string }>();
  const toast = useToast();
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ["resume", params.id], queryFn: () => getResume(params.id) });
  const [name, setName] = useState("");
  const [summary, setSummary] = useState("");

  useEffect(() => {
    if (query.data) {
      setName(query.data.name);
      setSummary(query.data.resume_data?.summary ?? "");
    }
  }, [query.data]);

  const save = useMutation({
    mutationFn: () =>
      updateResume(params.id, {
        name,
        resume_data: {
          summary,
          skills: query.data?.resume_data.skills ?? [],
          experience: query.data?.resume_data.experience ?? [],
          education: query.data?.resume_data.education ?? [],
          projects: query.data?.resume_data.projects ?? [],
        },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resume", params.id] });
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.notify("Resume updated");
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Failed", "error"),
  });

  if (query.isLoading) return <Spinner />;
  if (query.error || !query.data) return <ErrorState message="Resume not found." />;

  const resume = query.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">{resume.name}</h1>
        <p className="text-sm text-muted">
          Version {resume.version} · {resume.status} · {resume.is_default ? "Default" : "Not default"}
        </p>
      </div>
      <Card className="space-y-4">
        <Input label="Resume Name" value={name} onChange={(event) => setName(event.target.value)} />
        <Textarea
          label="Structured summary"
          value={summary}
          onChange={(event) => setSummary(event.target.value)}
        />
        <p className="text-sm text-muted">
          Structured resume data is the source of truth. File parsing will be added in a later sprint.
        </p>
        <div className="flex gap-2">
          <Button onClick={() => save.mutate()} disabled={save.isPending}>
            Save
          </Button>
          {resume.file_name ? (
            <Button variant="secondary" onClick={() => downloadResume(resume)}>
              Download file
            </Button>
          ) : null}
        </div>
      </Card>
      <Card>
        <h2 className="font-semibold">File metadata</h2>
        <dl className="mt-3 grid gap-2 text-sm md:grid-cols-2">
          <div>
            <dt className="text-muted">File name</dt>
            <dd>{resume.file_name ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-muted">Type</dt>
            <dd>{resume.file_type ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-muted">Size</dt>
            <dd>{resume.file_size ? `${Math.round(resume.file_size / 1024)} KB` : "—"}</dd>
          </div>
          <div>
            <dt className="text-muted">Status</dt>
            <dd>{resume.status}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
