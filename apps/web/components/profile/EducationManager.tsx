"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Input } from "@/components/ui/Input";
import { Spinner } from "@/components/ui/Spinner";
import { Textarea } from "@/components/ui/Textarea";
import {
  createEducation,
  deleteEducation,
  listEducation,
  updateEducation,
} from "@/lib/api/profile";
import { useToast } from "@/providers/ToastProvider";
import type { Education } from "@/types/api";

const schema = z.object({
  institution: z.string().min(1),
  degree: z.string().optional(),
  field_of_study: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  description: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

export function EducationManager() {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState<Education | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Education | null>(null);
  const query = useQuery({ queryKey: ["education"], queryFn: listEducation, retry: false });
  const form = useForm<FormValues>({ resolver: zodResolver(schema) });

  const save = useMutation({
    mutationFn: (values: FormValues) => {
      const payload = {
        ...values,
        degree: values.degree || null,
        field_of_study: values.field_of_study || null,
        start_date: values.start_date || null,
        end_date: values.end_date || null,
        description: values.description || null,
      };
      return editing ? updateEducation(editing.id, payload) : createEducation(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["education"] });
      toast.notify(editing ? "Education updated" : "Education added");
      setEditing(null);
      form.reset();
    },
    onError: (error) => toast.notify(error instanceof Error ? error.message : "Failed", "error"),
  });

  const remove = useMutation({
    mutationFn: (id: string) => deleteEducation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["education"] });
      toast.notify("Education deleted");
      setPendingDelete(null);
    },
  });

  if (query.isLoading) return <Spinner />;
  if (query.error) return <ErrorState message="Create a profile before adding education." />;

  const items = query.data ?? [];

  return (
    <div className="space-y-6">
      <Card>
        <h2 className="text-lg font-semibold">{editing ? "Edit education" : "Add education"}</h2>
        <form className="mt-4 space-y-4" onSubmit={form.handleSubmit((values) => save.mutate(values))}>
          <div className="grid gap-4 md:grid-cols-2">
            <Input label="Institution" {...form.register("institution")} />
            <Input label="Degree" {...form.register("degree")} />
            <Input label="Field of study" {...form.register("field_of_study")} />
            <Input label="Start Date" type="date" {...form.register("start_date")} />
            <Input label="End Date" type="date" {...form.register("end_date")} />
          </div>
          <Textarea label="Description" {...form.register("description")} />
          <Button type="submit">{editing ? "Update" : "Save education"}</Button>
        </form>
      </Card>

      {items.length === 0 ? (
        <EmptyState title="No education yet" description="Add degrees or certifications." />
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Card key={item.id} className="flex items-start justify-between">
              <div>
                <p className="font-semibold">{item.institution}</p>
                <p className="text-sm text-muted">
                  {[item.degree, item.field_of_study].filter(Boolean).join(" · ")}
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  onClick={() => {
                    setEditing(item);
                    form.reset({
                      institution: item.institution,
                      degree: item.degree ?? "",
                      field_of_study: item.field_of_study ?? "",
                      start_date: item.start_date ?? "",
                      end_date: item.end_date ?? "",
                      description: item.description ?? "",
                    });
                  }}
                >
                  Edit
                </Button>
                <Button variant="danger" onClick={() => setPendingDelete(item)}>
                  Delete
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete education"
        description="This education record will be removed."
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => pendingDelete && remove.mutate(pendingDelete.id)}
      />
    </div>
  );
}
