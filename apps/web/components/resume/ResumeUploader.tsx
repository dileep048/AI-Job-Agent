"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import { Button } from "@/components/ui/Button";
import { uploadResume } from "@/lib/api/resume";
import { useToast } from "@/providers/ToastProvider";

export function ResumeUploader() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const toast = useToast();
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["resumes"] });
      toast.notify("Resume uploaded");
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Upload failed", "error"),
  });

  function onFile(file: File | undefined) {
    if (!file) return;
    mutation.mutate(file);
  }

  return (
    <div
      className={`rounded-card border border-dashed p-8 text-center transition ${dragOver ? "border-[#FACC15] bg-ai-light" : "border-line bg-white"}`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragOver(false);
        onFile(event.dataTransfer.files[0]);
      }}
    >
      <p className="font-medium">Drag & drop resume here</p>
      <p className="mt-2 text-sm text-muted">PDF or DOCX · Maximum 10 MB</p>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        className="hidden"
        onChange={(event) => onFile(event.target.files?.[0])}
      />
      <Button className="mt-4" type="button" variant="secondary" onClick={() => inputRef.current?.click()}>
        Choose File
      </Button>
      {mutation.isPending ? <p className="mt-3 text-sm text-muted">Uploading...</p> : null}
    </div>
  );
}
