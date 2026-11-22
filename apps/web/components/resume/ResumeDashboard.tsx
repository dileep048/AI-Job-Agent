"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState } from "react";

import { ResumeUploader } from "@/components/resume/ResumeUploader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Spinner } from "@/components/ui/Spinner";
import { deleteResume, listResumes, setDefaultResume } from "@/lib/api/resume";
import { formatDate } from "@/lib/utils";
import { useToast } from "@/providers/ToastProvider";
import type { Resume } from "@/types/api";

export function ResumeDashboard() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [pendingDelete, setPendingDelete] = useState<Resume | null>(null);
  const query = useQuery({ queryKey: ["resumes"], queryFn: listResumes });

  const setDefault = useMutation({
    mutationFn: setDefaultResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.notify("Default resume updated");
    },
  });
  const remove = useMutation({
    mutationFn: (id: string) => deleteResume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.notify("Resume deleted");
      setPendingDelete(null);
    },
  });

  if (query.isLoading) return <Spinner />;
  if (query.error) return <ErrorState message="Could not load resumes." />;

  const resumes = query.data ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Resume Dashboard</h1>
        <p className="mt-1 text-sm text-muted">Upload files and keep structured resume data as the source of truth.</p>
      </div>
      <ResumeUploader />
      {resumes.length === 0 ? (
        <EmptyState
          title="No resume uploaded yet."
          description="Upload your resume to get started."
        />
      ) : (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">My Resumes</h2>
          {resumes.map((resume) => (
            <Card key={resume.id} className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="font-medium">{resume.name}</p>
                <p className="text-sm text-muted">
                  Version {resume.version} · Uploaded {formatDate(resume.created_at)} ·{" "}
                  {resume.is_default ? "Default" : "Not default"}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Link href={`/dashboard/resumes/${resume.id}`}>
                  <Button variant="secondary">View</Button>
                </Link>
                {!resume.is_default ? (
                  <Button variant="secondary" onClick={() => setDefault.mutate(resume.id)}>
                    Set Default
                  </Button>
                ) : null}
                <Button variant="danger" onClick={() => setPendingDelete(resume)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete resume"
        description="This file and its metadata will be removed."
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && remove.mutate(pendingDelete.id)}
      />
    </div>
  );
}
